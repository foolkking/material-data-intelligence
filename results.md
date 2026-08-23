# Task Results

## Production Object Management UX — 2026-08-20

状态：已完成

完成时间：2026-08-20

修改摘要：完成 Console 新建项目、Project/Data Navigator 右键与更多菜单、键盘/触摸等价入口、显式多选批量归档/恢复、可逆归档与空对象安全删除；补齐上传深链、Research Composer、Session/Message 写接口和 Report 归档的 Project 角色授权。只读成员仍可查看数据、研究结果和报告，但不会看到会失败的写入控件。

测试结果：完整 Python `1607 passed, 51 skipped, 75 warnings`；完整 Vitest `80 files / 525 tests passed`；聚焦管理/研究 `25 passed`；Project access/history `19 passed`；`npm run typecheck`、production build、compileall、`git diff --check` PASS。Chrome 已登录验收 Console 新建、Projects 分组/右键/Shift+F10/多选、Data 64 行真实表格、Dataset 菜单、Inspector 与焦点恢复；390px 验收同样通过，项目页、菜单、创建弹窗、数据表和 Inspector 均无横向溢出。

提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

## Production UI/UX Reconstruction — 2026-08-19 continuation

状态：处理中（核心闭环继续收敛）

完成时间：2026-08-19

修改摘要：修复 trajectory contract 对生产级数值矩阵的扫描误判；为 `viz.correlation` 增加严格、可审计的 pairwise evidence projector；将相关性 claim 投影为中文科研用户文案并将内部 correlation subject 从结果标题隐藏；重启 API 使用项目正确的 `uv run`/`--app-dir apps/api` 环境，完成真实 Q-TABLE Research Chrome 路径验证。保留了此前失败 turn、消息、Job、Artifact、Interpretation 和调用记录。

测试结果：`pytest tests/ -q` = 1584 passed, 51 skipped, 90 warnings；`npm run test -- --run` = 79 files / 494 tests passed；`npm run typecheck` PASS；`npm run build` PASS（仅既有 Plotly/glslify critical-dependency warnings）；`python -m compileall -q apps/api packages services tests` PASS；`git diff --check` 无 whitespace error。Chrome production route 实际确认：图表、数值表、中文 Pearson 相关系数发现、限制、依据和报告入口均可见，默认页面无 raw Plan/Tool/Job IDs。

CI/提交状态：未修改 `.github/workflows/**`，未部署；任务保持处理中，直至剩余科学 Viewer、增量结果浏览器观察、可访问性和最终产品验收债务关闭。

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

# Phase 10N-3 Experimental XRD Comparison + Peak Matching Result

## 1. Conclusion

`PASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.

## 2. N2 Baseline

N2 implementation `2b4dacf400400f5d1a68352d358346b4638d6cb9` / CI
`31258820229`, completion `3ffe6c5b85aca61402e4582654b0adfc0482a36b` /
CI `31260256371`, failed archive `a60c3bb89a98f35c76ea3f18c58670add96aa89b`
/ CI `31260829817`, and corrected archive
`4f5fa88354027a7b26842e9c71082fe567c84e13` / CI `31261360100` were
verified. Entry was clean master at the corrected archive, Registry 56 and task count 0.

## 3. Entry Gate

`PHASE_10N3_ENTRY_GATE=PASS`; N2 approval, ancestry, migration 0007, clean
HEAD/origin, queue, Registry and absence of N3/N4 production/tasks were verified.

## 4. N3-R0 Contract Closure

`PHASE_10N3_R0_CONTRACT_CLOSURE=PASS`; Tool, Resource, Profile, detector,
matcher, Artifact, identities, errors, references, tolerances and caps are exact,
with zero implementation-critical TBDs.

## 5. Acceptance Registry

N3-A01 through N3-A10 use the exact reviewer titles and definitions in all four
canonical documents.

## 6. N-D Decision Compliance

The existing authority chain, additive versioning, inert Artifact, exact binding,
server-side science, declarative Recipe and reviewer-gated phase order are preserved.

## 7. Production Behavior Changes

Added the approved experimental XRD resource/readiness, comparison Tool/Adapter,
Plan 0.2 integration, persisted result, Workspace surfaces and bounded delivery projections.

## 8. Registry 56 To 57

Exactly `structure.experimental_xrd_comparison@0.1.0` was added; final count is 57.

## 9. Theoretical XRD Authority

N3 consumes `structure.xrd@0.1.0` output contract `phase10e4.xrd_pattern.v1`.
`N3_THEORETICAL_XRD_REIMPLEMENTATION=0`.

## 10. Experimental XRD Resource Contract

`phase10n3.experimental_xrd_resource.v1` strictly binds versioned resource ID,
hash, degree-2theta axis, intensity semantics, angstrom wavelength and bounded points.

## 11. Units

Canonical units are degree 2theta and angstrom; no magnitude, filename or material-based inference exists.

## 12. Wavelength Semantics

Wavelength is explicit, finite, positive and bounded; mismatches are rejected without reprojection.

## 13. DataProfile Decision

DataProfile 2.2 is an additive, backward-compatible semantic extension. It stores
readiness facts only; Profile 2.1 remains readable and no bulk backfill occurs.

## 14. Eligibility

Eligibility distinguishes missing/ambiguous experimental semantics, producible or
persisted theory, wavelength mismatch, cap violations and platform availability.

## 15. Planner

Deterministic intents bind exact experimental and theoretical sources, tolerance
and detector parameters; multiple eligible sources require clarification.

## 16. AnalysisPlan 0.2

Existing theoretical Artifacts bind directly, or `structure.xrd` produces an exact
dependency consumed by N3. No generic DAG change was introduced.

## 17. PlanValidator

Wrong project/job/resource/Artifact/checksum/wavelength/contract/version and
unbounded parameters are rejected without automatic repair.

## 18. Experimental Data Validation

Strict validation covers finite equal-length monotonic arrays, explicit units,
minimum/maximum point counts, ranges, zero-only intensity and oversized input.

## 19. Normalization

The bounded allowlist is explicit and deterministic; source intensity semantics
remain distinct from normalized display values.

## 20. Peak Detection Algorithm

`mdi.experimental_xrd_peak_detection@1.0.0` uses locked SciPy 1.17.1
`scipy.signal.find_peaks` server-side.

## 21. Peak Detection Params

Strict bounded prominence, relative-height, separation and count fields reject
unknown, non-finite and out-of-range values; resolved defaults and hash persist.

## 22. Match-Independence Of Detection

Detection runs before and independently of theoretical matching.
`N3_MATCH_OPTIMIZED_PEAK_DETECTION=0`.

## 23. Theoretical Peak Contract

Exact persisted peak IDs, degree positions, relative intensities, hkl and
multiplicity are consumed with Tool/Artifact/wavelength/structure lineage.

## 24. hkl Semantics

N3 preserves theoretical hkl metadata and never recomputes indexing or labels an
experimental peak as definitively indexed.

## 25. Peak Matching Algorithm

`mdi.xrd_ordered_position_match@1.0.0` performs bounded deterministic one-to-one
position matching under an explicit degree-2theta tolerance.

## 26. One-To-One Constraint

Each experimental and theoretical peak participates in at most one pair.

## 27. Tie Handling

Canonical cost and identity ordering resolves exact ties deterministically without input-order authority.

## 28. Experimental Peak Identity

Identity binds resource hash, detector version/hash, canonical ordinal and exact detected position.

## 29. Theoretical Peak Identity

Identity binds theoretical Artifact checksum, producer, structure and formal peak ID.

## 30. Match Identity

Identity binds both exact peak identities, matcher version/hash, tolerance and N3 Artifact lineage.

## 31. Matched Peaks

Each pair retains both positions/intensities, theoretical hkl, signed and absolute delta 2theta.

## 32. Unmatched Experimental Peaks

All unmatched detected experimental peaks remain persisted and visible.

## 33. Unmatched Theoretical Peaks

All unmatched theoretical peaks remain persisted and visible.

## 34. Delta 2theta Residuals

Approved count/fractions, mean signed delta, MAE, RMSE, maximum and median absolute
delta are emitted only under their defined sample semantics; no refinement statistic exists.

## 35. Coverage

Point, detected, theoretical, matched, unmatched and excluded counts and fractions are explicit.

## 36. Zero-Match Behavior

Zero matches is a successful bounded comparison with explicit limitations, not a runtime failure.

## 37. Artifact Contract

`phase10n3.experimental_xrd_comparison.v1` stores exact refs plus bounded derived
series, peaks, matches, residuals, coverage, warnings and provenance without source duplication.

## 38. Determinism

Canonical point/peak/match/unmatched/warning order, serialization, hashes and checksums are tested.

## 39. Runtime

QueueWorkerRuntime resolves exact inputs, validates identity/checksum/units/caps,
runs the registered Adapter and persists inert output without network or arbitrary execution.

## 40. PostgreSQL

Exact-SHA CI `31270117864` verified job, ToolCall, dependency, Workspace and delivery persistence.

## 41. Redis

The same CI verified queue/events and blocked-descendant behavior without replanning.

## 42. MinIO

The same CI verified payload/checksum persistence and exact retrieval. Service
summary: 45 passed, 0 skipped, 0 failed, 0 errors.

## 43. Workspace

The metadata-first N3 panel exposes overlay, matched/unmatched tables, residuals,
warnings and provenance without browser scientific recomputation.

## 44. Overlay Plot

Experimental series, theoretical sticks, detected/matched/unmatched markers use
shape/text as well as color, with accessible table alternatives.

## 45. Selection

Exact experimental peak, theoretical peak and match selections bind project, job,
Artifact checksum, resources and peak identity; row/nearest/latest rebinding is absent.

## 46. Inspector

Inspector exposes exact sources, wavelengths, algorithms, params/hashes, peaks,
hkl, delta, coverage, warnings, limits and provenance.

## 47. Grounded Interpretation

The deterministic projector emits bounded counts, fractions, residuals, selected
facts, wavelength, tolerance and warnings; the LLM performs no detection or matching.

## 48. Scientific Wording

All surfaces state peak correspondence under the declared tolerance and explicitly
exclude refinement and definitive phase identification.

## 49. Report

Report composes persisted overlay/tables/residuals/coverage/provenance and the mandatory limitation statement.

## 50. Recipe

Recipe records exact source hashes, Tool/Artifact versions, detector/matcher params
and dependency bindings while remaining declarative and non-executable.

## 51. Historical Compatibility

No N3 backfill or read-time computation occurs; historical theory, Workspace,
Report, Recipe and selection contracts remain readable.

## 52. Reference Fixtures

Controlled perfect, shifted, missing, extra, competing, boundary, zero/single,
wavelength, unit, noisy, threshold and near-cap fixtures carry provenance.

## 53. Tolerances

Detection, matching, ties, residual regression, normalization and cross-platform
floating tolerances are quantity-specific; identities and checksums are exact.

## 54. Performance

Small, medium, near-cap and over-cap evidence verifies hard bounds for points,
peaks, candidates, matches, payload, plot points and timeout.

## 55. Plot Lifecycle

Fifty source/panel/selection cycles produced zero listener, observer, animation,
chart, request or stale-response growth.

## 56. Accessibility

Keyboard tables/selections, visible focus, non-color states, accessible legend and
summary, 44px mobile targets, 200% reflow and reduced motion pass.

## 57. Security

Untrusted data caps, finite/strict parsing, exact scope/checksum binding, inert
Artifacts and no code/shell/filesystem/network authority pass the N3 matrix.

## 58. LLM And DeepSeek

`NEW_LLM_CALL_SITES=0`; `N3_REQUIRES_LLM=NO`; `N3_REAL_LLM_CALLS=0`;
`DEEPSEEK_POLICY_REGRESSION=PASS`.

## 59. Browser Matrix

CI `31270117864` passed Chromium, Firefox, WebKit and Chromium 390x844 replay,
with zero console/page errors, unexpected responses, external requests or mobile overflow.

## 60. Tests

Corrected exact-SHA CI: backend 1210 passed, one documented environment skip and
46 deselected; frontend 430 passed; service-backed 45 passed with zero skipped,
failed or errors; typecheck, build, lock, migration, evidence and browsers passed.
Local Docker service-backed execution was unavailable; CI is the service authority.
`npm audit` remained UNAVAILABLE because the configured mirror returns 404_NOT_IMPLEMENTED.

## 61. Evidence

`docs/phase10n/evidence/phase10n3_experimental_xrd_comparison_peak_matching/`
contains authority, contracts, fixtures, runtime, browser, lifecycle, accessibility,
security and LF-normalized manifest evidence with zero missing/duplicate/secret entries.

## 62. Files Changed

Production changes are limited to approved N3 contracts and integrations.
Database schema = unchanged; migration = unchanged; migration head =
`0007_phase10m1_workspace_domain`; public API family = unchanged; dependencies =
unchanged; lockfile = unchanged.

## 63. Acceptance Results

Expected = 10; implemented = 10; missing = 0; extra = 0; duplicate registry
entries = 0; conflicting definitions = 0; canonical registry shorthand entries = 0.

## 64. Commit And CI History

- Initial implementation `1faa25582107ac3d34efea2e75b61ae3d0f9be13` / CI
  `31269467363`: failed one stale service selection-list assertion; all other jobs passed.
- Corrected implementation `5aef027d312f462eea72a1ced10b33e4f4664a50` /
  CI `31270117864`: success.
- Failed completion-record candidate `e805b8c8d41e69254da21b3209c600f8dce9aa34`
  / CI `31288217113`: one stale N2 lifecycle assertion; frontend/browser/build
  and service-backed 45/45 passed.
- Corrected completion record `c7547903faef191c97f35ca0ae2ad1ad1678193f` /
  CI `31288792343`: success.
- Queue-archive SHA/CI: this commit / pending exact-SHA CI.

## 65. Explicit Non-Scope

`N3_AUTOMATIC_PATTERN_SHIFT=0`; `N3_LATTICE_REFINEMENT=0`;
`N3_STRUCTURE_REFINEMENT=0`; `N3_RIETVELD_REFINEMENT=0`;
`N3_PHASE_FRACTION_REFINEMENT=0`; `N3_AUTOMATIC_PHASE_IDENTIFICATION=0`.
N4/N5 science, database search, external APIs and arbitrary execution are absent.

## 66. Queue State

After the queue-archive candidate, `TASK_BLOCK_COUNT=0`; the completed N3 task is
removed. Phase 10N-4 remains reviewer-gated and has no executable task.

## 67. Automatic N4 Entry

NO. `PHASE_10N4_EXECUTABLE_TASK_CREATED=NO`.

## 68. Final Repository State

At queue-archive creation, implementation authority is
`5aef027d312f462eea72a1ced10b33e4f4664a50` / CI `31270117864`, branch master,
migration head 0007, Registry 57 and task count 0. Completion authority is
`c7547903faef191c97f35ca0ae2ad1ad1678193f` / CI `31288792343`; queue-archive
exact-SHA verification is pending and N4 task is absent.

# Phase 10N-4 Trajectory RDF / MSD / Diffusion Result

## 1. Conclusion

`PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI`.

## 2. N3 Baseline

N3 implementation `5aef027d312f462eea72a1ced10b33e4f4664a50` / CI `31270117864`, completion `c7547903faef191c97f35ca0ae2ad1ad1678193f` / CI `31288792343`, and archive `0a33d84ea7c97b423f825f0c9784c57f1acfac3b` / CI `31289319532` were verified. Entry Registry was 57 and task count was zero.

## 3. Entry Gate

Master HEAD equaled origin, the worktree was clean, migration head was `0007_phase10m1_workspace_domain`, DataProfile was 2.2, and N4/N5 production/tasks were absent. `PHASE_10N4_ENTRY_GATE=PASS`.

## 4. N4-R0 Contract Closure

The three Tools, trajectory/time/cell/PBC authority, ASE/NumPy algorithms, strict params, Artifacts, identities, errors, references, tolerances and caps are exact; implementation-critical TBD count is zero.

## 5. Acceptance Registry

N4-A01 through N4-A10 are canonical and synchronized across acceptance, backlog, lock and manifest documents.

## 6. N-D Decision Compliance

The N0 scientific authority, bounded execution, exact identity, no-recomputation, wording, persistence and phase-order decisions remain intact.

## 7. Production Behavior Changes

Added approved trajectory RDF, server-unwrapped MSD, explicit-window diffusion diagnostics, additive readiness/planning, persisted Artifacts and Workspace/interpretation/Report integrations only.

## 8. Registry 57 To 60

Added exactly `trajectory.rdf@0.1.0`, `trajectory.msd@0.1.0`, and `trajectory.diffusion@0.1.0`; final Registry count is 60.

## 9. Existing Trajectory Authority Audit

Input authority is immutable `phase10g.trajectory.v1` with exact trajectory hash, stable atom order/IDs, frames, coordinates, units, cells, PBC and physical time.

## 10. Static RDF Boundary

Existing `structure.rdf` is unchanged. N4 trajectory RDF is an independent persisted authority and never averages frontend static-RDF output.

## 11. Trajectory Resource Contract

The strict resource validates bounded frames/atoms, stable atom records, explicit coordinate/wrapping semantics, cells/PBC and time metadata.

## 12. Frame Identity

Frame identity is trajectory hash plus formal frame index; playback index is not scientific authority.

## 13. Atom Identity

Atom identity is bound to the immutable trajectory and invariant atom record/order. Nearest-coordinate tracking is absent.

## 14. Species Identity

Species stability is validated across the immutable trajectory; mutation/reactive tracking is unsupported.

## 15. Time Semantics

Physical time is explicit, finite and strictly increasing, converted from fs to canonical ps where declared. MSD/diffusion reject missing or irregular production time.

## 16. Cell And PBC Semantics

Fixed/per-frame cells and exact three-axis PBC are explicit; partial PBC affects only enabled axes.

## 17. Variable-Cell Policy

RDF accepts validated per-frame cells only when every frame supports the requested safe radius. Initial MSD/diffusion reject variable cells.

## 18. Coordinate Semantics

Fractional versus Cartesian and wrapped versus unwrapped input are explicit contract fields and are never inferred from numeric range.

## 19. Unwrapping Algorithm

`mdi.fixed_cell_fractional_minimum_image@1.0.0` unwraps server-side with fixed-cell fractional continuity, triclinic mapping and partial-PBC handling.

## 20. Unwrapping Ambiguity

Post-wrap fractional steps at or above 0.49 produce `UNWRAPPING_AMBIGUOUS`; no perturbation, fallback or nearest-atom tracking occurs.

## 21. RDF Algorithm

`mdi.trajectory_rdf_ase_mic_unordered_pair_density@1.0.0` uses locked ASE 3.29.0 geometric minimum images and NumPy 2.4.6 bounded histograms.

## 22. RDF Normalization

Per-frame unordered-pair number-density and exact shell-volume normalization yields dimensionless `g(r)` with `r` in angstrom.

## 23. Species-Pair RDF

All-species, same-species and unordered cross-species pairs preserve explicit pair identity and self/double-count policy.

## 24. Window RDF

Whole, frame and physical-time windows use inclusive start/exclusive end and persist exact included frame identities and coverage.

## 25. RDF Safe Radius

Requested `rMax` must not exceed half the minimum periodic face spacing for any included frame; it is never silently clipped.

## 26. RDF Artifact

`phase10n4.trajectory_rdf.v1` persists source identity, params/hash, pair/window, exact bins, normalized values, counts, coverage, diagnostics and checksum.

## 27. MSD Estimator

`mdi.multiple_time_origin_msd@1.0.0` averages exact selected atoms and bounded time origins for each physical lag.

## 28. Total MSD

Total Cartesian MSD is persisted in angstrom squared with lag time in ps.

## 29. Species MSD

One exact species or all atoms is selected through formal trajectory species identity.

## 30. Directional MSD

Persisted x/y/z Cartesian components remain distinct and are not relabeled crystallographic a/b/c.

## 31. MSD Origin Coverage

Every lag records its origin count and coverage; low fit coverage prevents diffusion qualification.

## 32. Drift Correction Policy

Drift correction is explicitly `none`; no mass or center-of-mass authority is invented.

## 33. MSD Artifact

`phase10n4.trajectory_msd.v1` persists source, unwrapping policy/diagnostics, estimator, species, lag IDs/times, total/directional values, origins, limitations and checksum.

## 34. MSD To Diffusion Dependency

Diffusion consumes one exact persisted MSD Artifact through AnalysisPlan 0.2 binding by ID, contract, producer, checksum and trajectory lineage.

## 35. Fit Window

Start/end are explicit finite ps parameters. Missing windows require clarification; no automatic best-window selection exists.

## 36. Diffusion Regression

`mdi.explicit_window_ols_einstein@1.0.0` uses bounded NumPy OLS, `D=slope/6` for total and `D_axis=slope/2` for Cartesian directions.

## 37. Diffusive-Regime Diagnostics

Qualification requires minimum points/duration/origin coverage, positive slope, minimum R-squared, signal and a configured log-log alpha range.

## 38. Ballistic And Transient Rejection

Controlled constant-velocity MSD is `BALLISTIC_LIKE_WINDOW`; non-diffusive, poor, short or low-coverage windows retain diagnostics but no D estimate.

## 39. Diffusion Artifact

`phase10n4.trajectory_diffusion.v1` persists exact MSD lineage, fit window, fit values, diagnostics/status, qualified estimate or unavailable state, units and limitations.

## 40. Units

Distance is angstrom, time ps, MSD angstrom squared, RDF dimensionless and diffusion angstrom squared per ps.

## 41. DataProfile Decision

DataProfile 2.3 is an additive JSON-contract evolution for trajectory readiness facts. Profiles 2.2 and historical profiles remain readable; no result is profiled.

## 42. Eligibility

RDF, MSD and diffusion independently check their exact data/dependency prerequisites and caps without running scientific algorithms.

## 43. Planner

Deterministic intents cover whole/window/species RDF, total/species/directional MSD and explicit-window diffusion; ambiguous source/species/window requests do not choose latest/first.

## 44. AnalysisPlan 0.2

RDF/MSD bind trajectories directly; diffusion composes `trajectory.msd -> exact MSD Artifact -> trajectory.diffusion` or reuses an exactly compatible persisted MSD Artifact.

## 45. PlanValidator

Existing typed dependency validation rejects foreign/stale/checksum/contract/version/source/parameter mismatches and direct trajectory-to-diffusion bindings.

## 46. Runtime

Registered Adapters resolve bounded existing resources/Artifacts, compute server-side and persist through existing Runtime/Artifact authority with no network, shell, notebook or arbitrary path/code.

## 47. PostgreSQL

Exact-SHA CI `31299086998` passed N4 ToolCall/Artifact and dependency persistence through PostgreSQL.

## 48. Redis

Exact-SHA CI passed queue execution and typed dependency state through Redis.

## 49. MinIO

Exact-SHA CI passed exact MSD payload retrieval/checksum and N4 Artifact round trips through MinIO.

## 50. Workspace

The metadata-first Trajectory Analytics panel provides RDF, MSD and diffusion views with numeric tables and no frontend scientific computation.

## 51. Trajectory Viewer Integration

Exact trajectory identities link navigation and selection only; rendered positions never become displacement/RDF/MSD authority.

## 52. Selection

Six exact N4 kinds cover RDF pair/bin, MSD species/lag and diffusion window/diagnostic with Project/Workspace/Job/Artifact/checksum identity.

## 53. Inspector

Persisted algorithms, source trajectory/MSD, params/hash, units, values, origins, fit diagnostics, coverage, warnings and limitations are inspectable.

## 54. Interpretation

The deterministic projector exposes bounded persisted RDF/MSD/diffusion facts only; it performs no unwrapping, calculation, fitting or threshold selection.

## 55. Scientific Wording

Claims remain window-, estimator- and diagnostic-qualified; RDF peaks are not automatic bonds/shells and D is not an unconditional long-time bulk constant.

## 56. Report

Reports compose persisted plots/tables/diagnostics/provenance and disclose the explicit-window diffusion limitation; failed qualification emits no positive D conclusion.

## 57. Recipe

Recipes preserve exact trajectory, Tools/versions/params, unwrapping, MSD Artifact/checksum, fit window and dependency bindings and remain non-executable.

## 58. Historical Compatibility

No bulk backfill or read-time analytics occurs. Historical trajectory/Workspace/Report data remains readable and N4 is `NOT_AVAILABLE` without exact persisted N4 Artifacts.

## 59. References

Controlled lattice, boundary crossing, triclinic/partial-PBC, stationary, ballistic, random-walk, anisotropic/species, missing-time, variable-cell and fit fixtures are recorded.

## 60. Tolerances

Cell, coordinate, minimum-image, RDF, MSD, fit, R-squared, alpha and D tolerances are quantity-specific; trajectory/frame/atom/Artifact/Tool/parameter identities are exact.

## 61. Performance

Hard caps cover 200 frames, 5,000 atoms, 2,000,000 pair evaluations, 2,048 bins/lags, 4,096 origins, 10,000 fit points and 32 MiB Artifacts. Measurements are not capacity guarantees.

## 62. Viewer Lifecycle

Fifty view/species/window/selection cycles recorded zero WebGL/listener/observer/animation/canvas/chart/request/stale-response growth.

## 63. Accessibility

Complete RDF/MSD/fit tables, keyboard controls, visible focus, non-color series/status, 44px mobile controls, 200% reflow and reduced motion are covered.

## 64. Security

No arbitrary code, shell, filesystem, notebook, network or dynamic module authority exists. Scope/checksum binding, inert Artifacts, no frontend science and no automatic fit optimization pass.

## 65. LLM And DeepSeek

`NEW_LLM_CALL_SITES=0`; `N4_REQUIRES_LLM=NO`; `N4_REAL_LLM_CALLS=0`; `DEEPSEEK_POLICY_REGRESSION=PASS`.

## 66. Browser Matrix

Chromium, Firefox, WebKit and Chromium 390x844 passed locally and in CI `31299086998`, including N4 views, exact selections, lifecycle, accessibility and zero unapproved external requests.

## 67. Tests

Local backend: 1221 passed with 48 documented service/environment skips; frontend: 438 passed; typecheck/build passed. CI unit: 1220 passed, 1 documented environment skip, 47 integration deselected; service-backed: 46 passed, 0 skipped/failed/errors; all browser/build jobs passed. `npm audit=UNAVAILABLE` because the configured mirror returns `404_NOT_IMPLEMENTED`.

## 68. Evidence

`docs/phase10n/evidence/phase10n4_trajectory_rdf_msd_diffusion/` contains contracts, fixtures, persisted samples, runtime, browser, lifecycle, accessibility, security and LF-normalized hash manifest evidence.

## 69. Files Changed

Database schema = unchanged; migration = unchanged; migration head = `0007_phase10m1_workspace_domain`; public API family = unchanged; dependencies = unchanged; lockfile = unchanged; Workspace/Selection/Report/Recipe execution authorities are unchanged.

## 70. Acceptance Results

Expected = 10; implemented = 10; missing = 0; extra = 0; duplicate registry entries = 0; conflicting definitions = 0; canonical registry shorthand entries = 0.

## 71. Commit And CI History

- Failed implementation `3ae66528a7bffa596793fe6d72ea0e600819be8b` / CI `31298574230`: unit evidence hash failed across CRLF/LF; service 46/46 and frontend/browser passed.
- Corrected implementation `2965e585f22cb50ccae87f6d1e5860b5a1b5ba92` / CI `31299086998`: success.
- Completion record `ca5208feec772e45397f4afbb80419aa6263978f` / CI `31299648506`: success.
- Queue-archive SHA/CI: this commit / pending exact-SHA CI.

## 72. Explicit Non-Scope

No N5 Band/DOS/Fermi surface, Green-Kubo/VACF, Arrhenius, automatic fit window, variable-cell MSD, reaction/hop analysis, simulation/DFT/refinement, arbitrary execution, external scientific API, generic workflow, RAG, memory, multi-agent, plugin or enterprise capability was added.

## 73. Queue State

`TASK_BLOCK_COUNT=0`; the completed N4 task is removed and N5 remains reviewer-gated.

## 74. Automatic N5 Entry

NO. `PHASE_10N5_EXECUTABLE_TASK_CREATED=NO`; Phase 10N-5 remains `REVIEWER_GATE / NOT_QUEUED / NOT_EXECUTABLE`.

## 75. Final Repository State

Implementation authority is `2965e585f22cb50ccae87f6d1e5860b5a1b5ba92` / CI `31299086998`; completion authority is `ca5208feec772e45397f4afbb80419aa6263978f` / CI `31299648506`; queue-archive exact-SHA is pending. Branch is master, Registry count is 60, migration head is 0007, task count is zero and N5 executable task is absent.

Mandatory markers: `N4_RDF_FRONTEND_RECOMPUTATION=0`; `N4_MSD_FRONTEND_RECOMPUTATION=0`; `N4_DIFFUSION_FRONTEND_FIT=0`; `N4_MSD_WRAPPED_COORDINATE_DIRECT_USE=0`; `N4_DIFFUSION_RAW_TRAJECTORY_READS=0`; `N4_DIFFUSION_MSD_RECOMPUTATION=0`; `N4_AUTOMATIC_DIFFUSION_WINDOW_OPTIMIZATION=0`; `N4_BALLISTIC_SILENT_FIT=0`; `N4_TRANSIENT_SILENT_FIT=0`; `N4_MISSING_TIME_DIFFUSION=0`; `N4_VARIABLE_CELL_MSD_SILENT_ASSUMPTION=0`; `NEW_LLM_CALL_SITES=0`; `N4_REAL_LLM_CALLS=0`.

# Phase 10N-5 Electronic Band Structure + DOS Result

## 1. Conclusion

Phase 10N-5 is `PASS / COMPLETE / AWAITING_COMPLETION_RECORD_CI`. The implementation exact-SHA CI passed and the N5 task remains until the completion and archive gates close.

## 2. N4 Baseline

Verified archive `0442bf8925715efe81becaae19f21c58407a5a54` and its implementation/completion ancestry are authoritative; failed N4 candidate `3ae66528...` remains historical only.

## 3. Entry Gate

Entry verified master HEAD/origin, clean worktree, migration 0007, Registry 60, DataProfile 2.3, zero tasks and absent N5/N6 production/task state.

## 4. N5-R0 Contract Closure

R0 froze two Tools, supplied-resource schemas, energy/Fermi/spin semantics, exact identities, algorithms, Artifacts, errors, fixtures, tolerances and caps with zero critical TBDs.

## 5. Acceptance Registry

N5-A01 through N5-A10 are canonical: expected 10, implemented 10, missing/extra/duplicate/conflicting/shorthand 0.

## 6. N-D Decision Compliance

N0 scientific authority, auditability, no-browser-science, no-arbitrary-execution and no-secret boundaries remain intact.

## 7. Production Behavior Changes

Strict supplied Band/DOS resources now flow through Profile, Eligibility, Planner, validated Runtime, persisted Artifacts, Workspace, interpretation and Report/Recipe.

## 8. Registry 60 To 62

Exactly `electronic.band_structure@0.1.0` and `electronic.dos@0.1.0` were added. Combined Band+DOS presentation has Tool count 0.

## 9. Electronic Capability Audit

Existing electronic/BZ render foundations were reusable; no prior supplied-output Band/DOS Adapter or Artifact authority was treated as production N5 science.

## 10. Supplied Electronic Resource Boundary

Only strict immutable supplied electronic output is consumed. Platform electronic calculation authority is absent.

## 11. Band Resource Contract

`phase10n5.electronic_band_resource.v1` validates source/hash, calculation, structure binding, units/reference, Fermi, spin, reciprocal coordinates, path, k-points, bands and occupations.

## 12. DOS Resource Contract

`phase10n5.electronic_dos_resource.v1` validates source/hash, calculation, structure binding, energy/DOS semantics, Fermi, spin, total channels, projections and completeness.

## 13. Calculation Identity

Identity is resource-hash and formal calculation-identity bound; filename, title, upload order and latest selection have no authority.

## 14. Structure Binding

Formal structure ID/hash is preserved when supplied and never inferred.

## 15. Energy Units

Canonical energy is eV. Unknown units are rejected and no value-magnitude inference exists.

## 16. Energy Reference

`source_absolute` and `fermi_referenced` remain distinct; backend canonicalization is explicit and frontend alignment is prohibited.

## 17. Fermi Semantics

Fermi energy must be supplied. Missing Fermi preserves eligible raw views but disables Fermi-referenced features.

## 18. Spin Semantics

Non-spin-polarized and spin-polarized channels retain exact channel identity; no silent averaging, mirroring authority or noncollinear downgrade exists.

## 19. K-Point Identity

K-point identity binds exact Artifact/resource, formal ID, reciprocal coordinate and segment/path identity.

## 20. Reciprocal Coordinates

Fractional reciprocal coordinates and backend-supplied deterministic path distance are explicit; browser path reconstruction is absent.

## 21. K-Path Segments

Ordered segment IDs, endpoints, labels and breaks are persisted; path discontinuities are never connected.

## 22. Band Identity

Each band is exact Artifact + spin channel + formal band ID; ordinal/display labels are not cross-Artifact identity.

## 23. Band Energy Contract

Finite bounded supplied energies preserve source ordering without interpolation, dropping or connectivity optimization.

## 24. Band Gap Algorithm

`mdi.supplied_sampled_band_gap@1.0.0` deterministically derives sampled-data gap facts from supplied occupations/energies under the sealed 1e-5 eV threshold.

## 25. VBM And CBM

Persisted VBM/CBM facts retain energy, k-point, band and spin identity and are source-data qualified.

## 26. Direct And Indirect Gap

Directness compares exact sampled VBM/CBM k-point identities and is unavailable when formal identity is insufficient.

## 27. Metal-Like And Nonzero-Gap Classification

Only `METAL_LIKE_UNDER_POLICY`, `NONZERO_GAP_UNDER_POLICY` or unavailable is emitted; no definitive material class is claimed.

## 28. Band Artifact

`phase10n5.electronic_band_structure.v1` persists exact lineage, canonical data, gap facts, coverage, warnings, limitations, params/hash and checksum.

## 29. DOS Energy Grid

The finite strictly increasing supplied grid is validated and preserved without scientific resampling or smoothing.

## 30. DOS Unit And Normalization

States/eV/cell and source-defined relative semantics remain distinct; unknown normalization is never relabeled.

## 31. Total DOS

Formal total DOS must be supplied. Projections are not summed to invent it.

## 32. Spin DOS

Original spin channels and values remain separate; any mirrored visual convention is display-only and labeled.

## 33. Element Projected DOS

Only formally supplied element channels are retained with exact identities and coverage.

## 34. Orbital Projected DOS

Only allowlisted source-provided orbital channels are retained; no arbitrary merging or missing-channel generation occurs.

## 35. Projection Completeness

`COMPLETE`, `PARTIAL` and `UNKNOWN` are explicit. Partial/unknown data supports only statements about provided channels.

## 36. DOS Artifact

`phase10n5.electronic_dos.v1` persists exact lineage, grids/channels/projections, completeness, coverage, warnings, limitations, params/hash and checksum.

## 37. Band And DOS Compatibility

Combined presentation requires exact project, calculation/source, structure where present, unit/reference, Fermi and spin compatibility; mismatches do not combine.

## 38. Combined Presentation

Workspace consumes one exact Band Artifact and one exact DOS Artifact without a third Tool, recomputation, auto-shift or new truth.

## 39. DataProfile Decision

DataProfile 2.4 additively records electronic readiness only. Profiles 2.0-2.3 remain readable; no backfill, result profiling or migration occurs.

## 40. Eligibility

Band and DOS eligibility checks exact readiness, units, finite arrays, path/spin/projection semantics and caps without scientific execution.

## 41. Planner

Deterministic intents bind exact supplied resources; multiple candidates require clarification and never use first/latest/highest-match selection.

## 42. AnalysisPlan

Band and DOS are independent validated branches using existing plan semantics; combined display consumes their persisted outputs.

## 43. PlanValidator

Existing validation rejects foreign/stale/checksum/version/unit/spin/path/cap/completeness conflicts without repair.

## 44. Runtime

Registered Adapters validate, derive bounded summaries and persist through existing Runtime with no DFT, network, shell, notebook, dynamic module or arbitrary filesystem execution.

## 45. PostgreSQL

Exact-SHA CI `31311023072` passed N5 ToolCall/Artifact metadata persistence through PostgreSQL.

## 46. Redis

The same CI passed queue execution and state propagation through Redis.

## 47. MinIO

The same CI passed Band/DOS payload storage, retrieval and checksum through MinIO.

## 48. Workspace

The metadata-first Electronic Structure panel exposes Band, DOS and compatible combined views with numeric alternatives.

## 49. Band Viewer

Persisted curves, path breaks, labels, Fermi, VBM/CBM and gap facts render without frontend gap/path recomputation.

## 50. DOS Viewer

Persisted total/spin/projection channels, units/reference, Fermi and completeness render without frontend DOS computation.

## 51. Selection

Exact Band/DOS Artifact, k-point, band-state, gap, DOS channel/projection and energy-point selections bind Artifact/checksum/source/spin identities.

## 52. Inspector

Source, Tool/version, Artifact/checksum, units/reference, Fermi, spin, k-point/band/projection, values, policy, coverage, warnings and limitations are inspectable.

## 53. Grounded Interpretation

The deterministic projector exposes only persisted bounded Band/DOS facts; the LLM performs no gap, completeness, alignment or spin computation.

## 54. Scientific Wording

All claims are qualified as derived from supplied data under stated policy; no true/experimental gap, definite metal class or platform-calculated electronic structure is claimed.

## 55. Report

Reports compose persisted figures/tables/provenance and disclose that the platform does not perform DFT/GW in this capability.

## 56. Recipe

Recipes preserve exact resource hashes, Tools/versions/params, units/reference, spin, completeness and Artifact bindings and remain non-executable.

## 57. Historical Compatibility

No backfill or read-time electronic analysis occurs. Incomplete legacy contracts are read-only or typed unsupported; N5 is unavailable without persisted N5 Artifacts.

## 58. References

Controlled gapped, gapless, direct, indirect, spin, path-break, missing-Fermi, total/projected/partial DOS, compatibility and near-cap fixtures are recorded.

## 59. Tolerances

Energy, Fermi, gap, VBM/CBM, reciprocal coordinate, DOS and threshold tolerances are quantity-specific; all scientific identities and hashes are exact.

## 60. Performance

Hard caps bound k-points, bands, spin channels, segments, DOS points, projection channels, output bytes, plotting points, timeout and memory; small/medium/near/over-cap evidence is recorded.

## 61. Plot Lifecycle

Fifty Band/DOS/combined/spin/projection/selection cycles record zero listener, observer, animation, duplicate-chart/request and stale-response growth.

## 62. Accessibility

Numeric table alternatives, keyboard selections, visible focus, non-color spin distinction, textual path/gap/completeness, 44px mobile controls, reflow and reduced motion are covered.

## 63. Security

Arbitrary execution, DFT/GW, Fermi surface, projected bands, frontend science, cross-scope rebinding, executable Artifact content and secret/path disclosure gates pass.

## 64. LLM And DeepSeek

`NEW_LLM_CALL_SITES=0`; `N5_REQUIRES_LLM=NO`; `N5_REAL_LLM_CALLS=0`; `DEEPSEEK_POLICY_REGRESSION=PASS`.

## 65. Browser Matrix

CI `31311023072` passed N5 Chromium, Firefox, WebKit and Chromium 390x844 replay: `PHASE10N5_CHROMIUM_FIREFOX_WEBKIT_PASS` and `PHASE10N5_CHROMIUM_390X844_PASS`.

## 66. Tests

Local backend: 1242 passed with 49 documented service/environment skips; CI unit: 1242 passed, 1 environment skip, 48 integration deselected; frontend local: 449 passed; service-backed: 47 passed, 0 skipped/failed/errors; typecheck/build/browser passed. npm audit remains unavailable because the configured mirror returns `404_NOT_IMPLEMENTED`.

## 67. Evidence

`docs/phase10n/evidence/phase10n5_electronic_band_dos/` contains R0, contracts, fixtures, samples, planner/runtime, browser, lifecycle, accessibility, security and checksum-manifest evidence.

## 68. Files Changed

Production contracts/Adapters/Profile/Registry/Planner/Runtime/Workspace/projector plus tests/docs/evidence changed. Database schema, migration, public API family, dependencies and lockfile are unchanged.

## 69. Acceptance Results

N5 acceptance is 10/10; Registry is 62; implementation-critical TBDs are zero.

## 70. Commit And CI History

- Implementation `34bcea5bd3672d91f3282e12dd5a0cb6b789f1ff` / exact-SHA CI `31311023072`: success.
- Failed completion candidate `49da783610887c29ee01307884f45f2d9096b287` / CI `31311662979`: unit job found two retained N1/N2 queue assertions that did not allow the approved N5 completion-waiting status; service-backed and frontend/browser/build jobs passed.
- Corrected completion-record SHA/CI: this commit / pending exact-SHA CI.
- Queue-archive SHA/CI: pending after completion CI.

## 71. Explicit Non-Scope

No N6, DFT/SCF/NSCF/GW/scissor, Band/DOS generation, Fermi surface, projected bands/fatbands, Wannier, transport, effective mass, charge/Bader/topology, arbitrary execution, external scientific API, generic workflow, RAG, memory, multi-agent, plugins or enterprise capability was added.

## 72. Queue State

`TASK_BLOCK_COUNT=1`; N5 remains retained until completion and archive exact-SHA CI pass.

## 73. Automatic N6 Entry

NO. `PHASE_10N6_EXECUTABLE_TASK_CREATED=NO`; Phase 10N-6 remains `REVIEWER_GATE / NOT_QUEUED / NOT_EXECUTABLE`.

## 74. Final Repository State

At completion-record creation: branch master, implementation authority `34bcea5bd3672d91f3282e12dd5a0cb6b789f1ff` / CI `31311023072`, Registry 62, migration head 0007, task count one retained N5 task, N6 executable task absent. Completion and archive exact-SHA authority remain pending.

Mandatory markers: `N5_PLATFORM_DFT_EXECUTION=0`; `N5_PLATFORM_GW_EXECUTION=0`; `N5_BAND_GENERATION_FROM_STRUCTURE=0`; `N5_DOS_GENERATION_FROM_STRUCTURE=0`; `N5_DOS_GENERATION_FROM_BANDS=0`; `N5_FERMI_SURFACE_GENERATION=0`; `N5_PROJECTED_BAND_ANALYSIS=0`; `N5_FRONTEND_BAND_GAP_RECOMPUTATION=0`; `N5_FRONTEND_DOS_RECOMPUTATION=0`; `N5_FRONTEND_ENERGY_ALIGNMENT_AUTHORITY=0`; `N5_FRONTEND_SPIN_MERGING_AUTHORITY=0`; `NEW_LLM_CALL_SITES=0`; `N5_REAL_LLM_CALLS=0`.

Boundary markers: database schema = unchanged; migration = unchanged; migration head = `0007_phase10m1_workspace_domain`; public API family = unchanged; dependencies = unchanged; lockfile = unchanged; Registry count = 62.

# Phase 10N-6 Professional Capability Integration + Evidence Closure Result

## 1. Conclusion
N6 integration and evidence implementation is complete within sealed N1-N5 scientific contracts. Corrected implementation exact-SHA CI passed; completion-record and archive CI remain lifecycle gates.

## 2. N5 Baseline
Verified N5 archive `2496d7a9ceb61d016f0f8d6a7f3fdd4572df3295` / CI `31312979614` is the sole entry authority. Failed completion `49da783610887c29ee01307884f45f2d9096b287` is historical only.

## 3. Entry Gate
Master, HEAD/origin equality, clean worktree, ancestry, Registry 62, DataProfile 2.4, migration 0007 and zero queued tasks passed at entry.

## 4. N6-R0 Integration Closure
The nine-Tool inventory, integration/evidence matrices and zero-new-science boundary are exact; implementation-critical TBDs are zero.

## 5. Acceptance Registry
N6-A01 through N6-A10 are implemented exactly once in each canonical authority document: 10/10, missing/extra/duplicate/conflicting zero.

## 6. Phase 10N Tool Inventory
N1 contributes CrystalNN/VoronoiNN; N2 local environment; N3 XRD comparison; N4 RDF/MSD/diffusion; N5 Band/DOS: nine professional Tools total.

## 7. Registry 62 Preservation
`REGISTRY_BEFORE_N6 = 62`; `REGISTRY_AFTER_N6 = 62`; N6 adds no Tool.

## 8. DataProfile 2.4 Closure
Profiles 2.0-2.4 remain readable and 2.4 covers all approved readiness facts without results or backfill. `DATAPROFILE_BEFORE_N6 = 2.4`; `DATAPROFILE_AFTER_N6 = 2.4`.

## 9. N1-N5 Capability Matrix
Every professional Tool maps Profile facts, Eligibility, Planner metadata, ports, Adapter, Artifact, identity, units, renderer, selection, projector, Report/Recipe and evidence; unmapped Tools are zero.

## 10. AnalysisIntent Coverage
Coordination, local environment, XRD, RDF, MSD, diffusion, Band/gap, DOS/projected DOS and clarification/unsupported/mismatch routes are covered.

## 11. Eligibility Coverage
Exact prerequisites and typed unavailable/incompatible states are validated without executing scientific algorithms.

## 12. Planner Coverage
Capability-aware routing uses Intent, Profile, metadata, Eligibility and exact bindings; negative cross-domain routing passes.

## 13. Source Ambiguity Behavior
Multiple structures, XRD resources, trajectories or electronic resources produce clarification, never latest/first/best binding.

## 14. AnalysisPlan 0.1 Compatibility
Plan 0.1 remains readable and unchanged.

## 15. AnalysisPlan 0.2 Dependency Closure
N1-to-N2, theoretical-XRD-to-N3 and MSD-to-diffusion ports preserve producer output contract, checksum and consumer input identity.

## 16. PlanValidator Closure
Wrong scope, identity, checksum, Tool/contract version and stale/foreign sources are typed rejected without repair.

## 17. QueueWorkerRuntime Closure
Positive cases persist Intent, Eligibility, Plan, Job, ToolCall, Adapter output, Artifact, lineage and terminal state through the real Runtime.

## 18. Partial Execution Closure
Producer failure blocks descendants while independent branches remain available; no fallback, replan or silent rerun occurs.

## 19. Artifact Contract Inventory
All N1-N5 Artifact families expose exact type/version, producer, sources, params, units, coverage, warnings, limitations, checksum and lineage.

## 20. Artifact Lineage
Artifact dependencies are checksum-bound and source-scoped; recomputation does not cross sealed dependency boundaries.

## 21. Identity Matrix
Structure/site/neighbor/environment/polyhedron, XRD, trajectory and electronic identities are exact; array position, display label, filename, nearest/fuzzy and latest authority are none.

## 22. Unit Matrix
Angstrom, degree, dimensionless coordination/RDF, ps, angstrom^2, angstrom^2/ps, eV and source-qualified DOS/reciprocal semantics are explicit.

## 23. Scientific Wording Audit
Production wording remains algorithm/source/tolerance/window-qualified; definitive bonding, phase confirmation, unconditional diffusion and platform-DFT claims are rejected.

## 24. N1 Coordination E2E
Periodic structure through Profile/Intent/Eligibility/Planner/Runtime/Artifact/Workspace/interpretation/Report/Recipe passes.

## 25. N1 Algorithm Independence
CrystalNN and VoronoiNN remain distinct authorities with no merge, rank or winner selection.

## 26. N2 Local Environment E2E
Exact N1 Artifact dependency through polyhedron Artifact and delivery surfaces passes.

## 27. N1-to-N2 Dependency Integrity
`N2_RECOMPUTED_N1_NEIGHBORS = 0`; `N2_INDEPENDENT_NEIGHBOR_SEARCH = 0`; `N2_COORDINATION_ALGORITHM_FALLBACK = 0`.

## 28. N3 Experimental XRD E2E
Experimental resource plus exact theoretical Artifact produces matched/unmatched peaks, residuals and persisted delivery evidence.

## 29. N3 Zero-Match / Wavelength Negative Cases
Zero matches is a valid scientific result; wavelength mismatch is typed incompatible. `N3_THEORETICAL_XRD_REIMPLEMENTATION = 0`; `N3_AUTOMATIC_PATTERN_SHIFT = 0`; `N3_RIETVELD_REFINEMENT = 0`; `N3_AUTOMATIC_PHASE_IDENTIFICATION = 0`.

## 30. N4 RDF E2E
Exact trajectory species/window RDF passes Profile through Report/Recipe with persisted bins, normalization and coverage.

## 31. N4 MSD E2E
Server-side unwrapping, physical time, total/species/directional MSD and origin coverage pass.

## 32. N4 Diffusion E2E
Diffusion consumes exact persisted MSD with explicit fit window and diagnostics. `N4_DIFFUSION_RAW_TRAJECTORY_READS = 0`; `N4_DIFFUSION_MSD_RECOMPUTATION = 0`.

## 33. N4 Ballistic Negative Case
MSD remains valid while qualification is unavailable: `N4_MSD_WRAPPED_COORDINATE_DIRECT_USE = 0`; `N4_AUTOMATIC_DIFFUSION_WINDOW_OPTIMIZATION = 0`; `N4_BALLISTIC_SILENT_FIT = 0`; `N4_MISSING_TIME_DIFFUSION = 0`.

## 34. N5 Band E2E
Supplied Band Resource produces exact Band Artifact, sampled gap/VBM/CBM/directness/classification and delivery evidence.

## 35. N5 DOS E2E
Supplied DOS Resource preserves total/spin/projection completeness and exact delivery evidence.

## 36. N5 Band+DOS Combined Presentation
Compatible persisted Artifacts combine without a third Tool or browser alignment; incompatible sources do not combine.

## 37. Workspace Integration
Each Job retains one metadata-first Workspace; inactive heavy payload requests are zero and active loads are cancellable with stale suppression.

## 38. Canonical Selection
All stable selections are exact; renderers without stable identities remain consumer-only and prohibited cross-science mappings are absent.

## 39. Inspector
Professional panels expose Tool/version, Artifact/checksum, source hashes, algorithms, params, units, coverage, warnings, limitations and lineage.

## 40. Grounded Interpretation
Each Artifact family has deterministic bounded projection or an explicit disposition; providers receive facts rather than raw scientific authority.

## 41. Grounding Negative Cases
Invented values/units/entities/thresholds and bonding, confirmation, unqualified diffusion or platform-DFT claims are rejected.

## 42. Report Closure
Reports compose persisted facts with coverage/warnings/limitations/provenance. `REPORT_GENERATED_SCIENTIFIC_VALUES = 0`; `REPORT_GENERATED_SCIENTIFIC_CLAIMS = 0`; `REPORT_SCIENTIFIC_RECOMPUTATION = 0`.

## 43. Recipe Closure
Recipes preserve Profile/Intent/Eligibility/Plan/Tool/params/dependencies/contracts/sources and remain declarative. `RECIPE_EXECUTION_AUTHORITY = NONE`; plan/job/queue authority is none.

## 44. Historical Compatibility
Profiles 2.0-2.4, Plans 0.1/0.2, historical Jobs/Workspaces/Artifacts/Reports/Recipes remain readable without backfill or read-time science; historical rebinding is zero.

## 45. Phase 10K/L/M Regression
Generic Profile, Explorer, ML, Composition, Intent, Eligibility, Plans, interpretation, Workspace/selection/gallery and Report/Recipe regressions pass; one-Workspace-per-Job and migration authority are unchanged.

## 46. PostgreSQL
Exact-SHA CI persisted and scoped professional resources, ToolCalls, Artifacts, dependencies and Workspaces successfully.

## 47. Redis
Queue/runtime and dependency behavior passed service-backed closure.

## 48. MinIO
Artifact payload/checksum persistence and retrieval passed service-backed closure.

## 49. Browser Matrix
Chromium, Firefox and WebKit professional-family replays pass with zero console/page/unexpected-response/external-request errors.

## 50. Mobile
Chromium 390x844 covers structure, XRD, trajectory and electronic families without horizontal overflow.

## 51. Accessibility
Keyboard/focus, named controls, non-color state, tables/text alternatives, 44px targets, 200% reflow and reduced motion pass.

## 52. Performance
Small/medium/near-cap/over-cap evidence and bounded E2E timings/Artifact bytes/load/projection/report metrics are retained as development evidence, not an SLA.

## 53. Viewer Lifecycle
Fifty cross-panel cycles show zero WebGL/listener/observer/animation/canvas/chart/request/stale-response growth.

## 54. Security
Arbitrary code, shell/filesystem/notebook/network/dynamic module, executable Artifact content, cross-scope/stale/latest/fuzzy binding and secret/path/stack/storage disclosure gates pass.

## 55. LLM / DeepSeek
`N6_NEW_LLM_CALL_SITES = 0`; `N6_REAL_LLM_CALLS_DEFAULT_CI = 0`; N6 requires no LLM and DeepSeek policy regression passes.

## 56. References / Fixtures
N1-N5 retained references plus newly replayed critical positive and negative integration fixtures are inventoried in the N6 manifest.

## 57. Tolerance Closure
Existing quantity-specific tolerances are preserved; N6 changes no formula, threshold, default or scientific parameter.

## 58. Evidence Inventory
The N6 evidence tree contains baseline/R0/acceptance, capability/tool/Profile/Planner/Plan/Artifact/identity/unit matrices, E2E/negative/historical/delivery/service/browser/performance/accessibility/security records.

## 59. Evidence Manifest Integrity
Normalized manifest validation reports entries present, missing/extra/hash mismatch/secret-bearing evidence zero; screenshots are not numeric authority.

## 60. Documentation Closure
N6 contracts, matrices, evidence map, completion, final summary and Phase 11 reviewer gate are documented; canonical and persistent authorities are synchronized.

## 61. Files Changed
N6 changed integration tests, aggregate CI/browser/service gates, evidence and documentation only; no scientific production authority was added.

## 62. Production Behavior Changes
Linux browser-server process-group cleanup and CI build ordering prevent lifecycle resource accumulation without changing scientific behavior or test coverage.

## 63. Acceptance Results
N6 acceptance 10/10; backend 1252 passed, frontend 449 passed, service-backed 48 passed with zero skipped/failed/errors, browser/typecheck/build/lock/security/evidence passed. npm audit is UNAVAILABLE because the configured mirror returns `404_NOT_IMPLEMENTED`.

## 64. Phase 10N Final Readiness
Coordination, Local Environment/Polyhedra, Experimental XRD, trajectory RDF/MSD/Diffusion and electronic Band/DOS are each `READY_WITH_EXPLICIT_LIMITS`.

## 65. Commit / CI History
- Failed implementation `ea156ed898ce7c2ed539a026f2983b239e444d8a` / CI `31315296903`: build cancellation after accumulated browser servers; retained historical only.
- Corrected implementation `eda7cda4d14207abaf97a0a88cc263b0d1ad3319` / CI `31316556495`: success.
- Completion-record SHA/CI: this commit / pending exact-SHA CI.
- Verified queue-archive SHA/CI: pending after completion CI.

## 66. Explicit Remaining Limits
No bond-valence/oxidation inference, Rietveld/refinement/phase fraction/automatic phase identification, unsupported variable-cell MSD, Green-Kubo/VACF/Arrhenius, DFT/GW/Fermi surface/projected bands/Bader/defects/surfaces, arbitrary execution, generic workflow or autonomous scientific agent.

## 67. Queue State
`TASK_BLOCK_COUNT = 1`; the completed N6 task remains until completion-record and archive exact-SHA CI pass.

## 68. Phase 11 Gate
Phase 11 is `REVIEWER_GATE / NOT QUEUED / NOT EXECUTABLE`; `PHASE11_EXECUTABLE_TASK_CREATED = NO`.

## 69. Final Repository State
At completion-record creation: master, implementation authority `eda7cda4d14207abaf97a0a88cc263b0d1ad3319` / CI `31316556495`, Registry 62, DataProfile 2.4, migration head 0007, one retained N6 task. The verified archive gate remains pending.

Mandatory N6 markers: `N6_NEW_SCIENTIFIC_TOOLS = 0`; `N6_NEW_SCIENTIFIC_ALGORITHMS = 0`; `N6_NEW_ARTIFACT_FAMILIES = 0`; `N6_NEW_DATAPROFILE_VERSION = 0`; `N6_NEW_PUBLIC_API_FAMILIES = 0`; `N6_NEW_DATABASE_MIGRATIONS = 0`; `N6_NEW_DEPENDENCIES = 0`; `N6_NEW_LLM_CALL_SITES = 0`; `N6_REAL_LLM_CALLS_DEFAULT_CI = 0`.

Authority markers: `FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE`; `FRONTEND_SCIENTIFIC_RECOMPUTATION = NONE`; `WORKSPACE_SCIENTIFIC_AUTHORITY = NONE`; `REPORT_SCIENTIFIC_RECOMPUTATION = 0`; `RECIPE_EXECUTION_AUTHORITY = NONE`; `N5_PLATFORM_DFT_EXECUTION = 0`; `N5_PLATFORM_GW_EXECUTION = 0`; `N5_BAND_GENERATION_FROM_STRUCTURE = 0`; `N5_DOS_GENERATION_FROM_STRUCTURE = 0`; `N5_FERMI_SURFACE_GENERATION = 0`; `N5_PROJECTED_BAND_ANALYSIS = 0`.

Repository boundaries: database schema = unchanged; migration = unchanged; migration head = `0007_phase10m1_workspace_domain`; public API family = unchanged; dependencies = unchanged; lockfile = unchanged; Registry count = 62; DataProfile = 2.4.

# Phase 11-0 Validation Baseline Reconciliation + Governance Seal Result

## 1. Conclusion
PASS. Phase 11-0 reconciled the current validation baseline and sealed governance without production scientific changes. Implementation `312fd4445d404f0f89c061fbdc055789912dc552` passed exact-SHA CI `31324356338`.

## 2. Phase 10N Baseline
N6 verified archive `d4d625b57449f9a451d5e27a6eb903625d221bc7` is the sole entry authority; failed N6 `ea156ed...` remains historical only.

## 3. Entry Gate
Master, clean entry worktree, `HEAD == origin/master`, N6 ancestry, Registry 62, DataProfile 2.4, migration 0007, and zero queued tasks passed before admission.

## 4. Gate J6-R Roadmap Authority Reconciliation
Repository/current reviewer authority supersedes stale phase-generated next-scope numbering without rewriting history.

## 5. Approved Phase 11 / 12 / 13 Roadmap
Phase 11 is scientific validation; Phase 12 is comprehensive UI/UX redesign; Phase 13 is final product closure. Old Phase 12 final-closure numbering is superseded.

## 6. Production Behavior Changes
`PRODUCTION_BEHAVIOR_CHANGES = NONE`; only docs, persistent state, evidence, deterministic audit tooling, and audit consistency tests changed.

## 7. Registry Inventory
All 62 live Registry entries were read from the three manifests and reconciled against Adapter declarations.

## 8. Registry Count 62 Verification
`REGISTRY_BEFORE_11_0 = 62`; `REGISTRY_AFTER_11_0 = 62`; unique rows 62; duplicate/unclassified rows 0.

## 9. Tool Role Classification
Rows cover scientific numeric/geometry/classification/transformation, data intelligence, materials ML, composition, visualization-data, product composition, presentation, and metadata/utility roles.

## 10. Validation Dimension Model
Software execution, scientific reference, numeric validation, Artifact contract, platform integration, browser presentation, reproducibility, and known limitations are independent axes.

## 11. Current Validation Level Distribution
28 rows are conservatively V2 controlled-reference and 34 V1 runtime/Artifact; Phase 11-0 promotes none to V3/V4.

## 12. Existing Evidence Inventory
Ten Phase 10 evidence roots were indexed with file, manifest, browser, service, and reference indicators.

## 13. Existing Reference Inventory
43 reference-like retained records were hashed and classified; no reference was downloaded.

## 14. Reference Provenance Classification
Analytic, official-library/project, independent cross-library, controlled synthetic, internal expected, mapping-only, and no-reference types are sealed.

## 15. Reference Independence Audit
Self-reference remains regression evidence only; reference authority follows provenance/hash/contract, not recency.

## 16. Existing Fixture Inventory
169 fixture records were indexed with stable path/hash and review disposition.

## 17. Fixture Immutability Policy
Authoritative fixtures cannot be overwritten in place; source/value/transformation changes require a new version.

## 18. Fixture License Status
Repository-internal versus `LICENSE_REVIEW_REQUIRED` is recorded; no legal status is inferred.

## 19. Official Example Historical Inventory
54 official/example records were indexed, including retained Phase 10F mappings.

## 20. Current Official Example Status
Records distinguish current, retained historical, mapping-only, extraction-required, and superseded status; none was executed here.

## 21. Input / Resource / Parser Inventory
Upload/sniffing, parser, Resource, Profile, Planner, Runtime, Workspace, caps, and negative paths were audited.

## 22. Supported Input Matrix
CSV/CIF/POSCAR are direct; canonical JSON, XYZ/EXTXYZ, volumetric, ZIP, and supplied electronic JSON are bounded; phonon direct upload is mapping-only; XLSX, Parquet, and LAMMPS trajectory are unsupported.

## 23. DataProfile 2.4 Input Coverage
Profile 2.4 remains unchanged and records readiness only, never validation results.

## 24. Planner / Eligibility Input Coverage
Support requires an actual parser/resource/profile path; library theoretical format support is insufficient.

## 25. Runtime / Workspace Input Coverage
Runtime and renderer disposition are separate from parsing and mapping status.

## 26. Scientific Numeric Validation Inventory
Numeric Tools retain analytic/controlled/internal distinctions and quantity-owned tolerances.

## 27. Scientific Geometry Validation Inventory
Structure, local geometry, reciprocal-cell, and periodic identity evidence remains explicit; independent gaps are assigned.

## 28. Product / Presentation Validation Inventory
These require contract, exact source, no recomputation, deterministic rendering, accessibility, and security rather than invented numeric benchmarks.

## 29. N1 Validation Baseline
CrystalNN/VoronoiNN algorithm identity, neighbors, weights, coordination, distance, determinism, and disagreement semantics are inventoried; mutual equality is not required.

## 30. N2 Validation Baseline
Exact N1 dependency, geometry, distortion, hull, tie, periodic identity, and synthetic controls are retained.

## 31. N3 Validation Baseline
Input validation, detection, normalization, one-to-one matching, ties, residuals, unmatched sets, zero-match, wavelength mismatch, and coverage are retained. Correspondence is not phase confirmation.

## 32. N4 Validation Baseline
Unwrapping, PBC, RDF, MSD, directional/origin coverage, diffusion diagnostics, ballistic rejection, random walk, missing time, and variable-cell policy are classified by evidence strength.

## 33. N5 Validation Baseline
Energy/Fermi/spin/path/band/gap/DOS/projection/compatibility controls validate supplied output, not platform DFT.

## 34. Earlier Initial-Release Science Validation Baseline
Composition, statistics, Dataset Explorer, ML, PCA/KMeans, structure summaries, static RDF/XRD, trajectory presentation, phonon, BZ, and volumetric capabilities are included.

## 35. Tolerance Inventory
Identity exactness plus N1-N5, phonon, and BZ quantity-specific policies are indexed.

## 36. Tolerance Ownership
Every tolerance records contract, metric, unit, provenance, reason, owner, justification, variance relevance, and review state.

## 37. Exact Identity Rules
Tool/version, hashes, checksums, Plan bindings, site/atom/frame/k-point/band/evidence identities remain exact.

## 38. Variance Classification
Only `EXACT`, `TOLERANCE_BOUNDED`, `DISPLAY_ONLY_VARIANCE`, `UNSUPPORTED_PLATFORM`, and `KNOWN_LIMITATION` are allowed.

## 39. Revalidation Triggers
Scientific versions/algorithms/default semantics/contracts/units/parsers/authority dependencies/fixtures/tolerances/identity changes invalidate relevant validation.

## 40. Locked Environment Policy
Primary scientific environment is the current repository lock; arbitrary dependency-version compatibility is not claimed.

## 41. Cross-Platform Target Matrix
Locked Linux CI and Windows are targets; macOS is not a current release target absent separate support evidence.

## 42. Browser Validation Boundary
Chromium, Firefox, WebKit, and 390x844 validate presentation/interaction/no recomputation, not numeric truth.

## 43. Service Validation Boundary
PostgreSQL/Redis/MinIO validate persistence, queue, Artifact storage, identity, lineage, scope, and checksum, not numeric truth.

## 44. Screenshot Authority Boundary
`SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE`.

## 45. Validation Gaps
Twelve concrete provenance, independent benchmark, variance, and honest coverage gaps were recorded; no catch-all gap exists.

## 46. Gap Prioritization
P0=0; release-relevant P1 and supporting P2 gaps are assigned to exact Phase 11 stages.

## 47. Phase 11-1 Backlog
Exact official/static sources, fixtures, source/license checksums, and transformation requirements are sealed; no numeric PASS is authorized.

## 48. Phase 11-2 Backlog
Exact Tool/version, fixture, expected invariant/value, unit, tolerance, positive/negative case, and 11-1 dependency fields are documented.

## 49. Phase 11-3 Matrix
Locked Linux/Windows scientific variance and four-browser presentation invariants use the sealed variance taxonomy.

## 50. Phase 11-4 Coverage Rules
`DIRECT_VERIFIED`, `OFFICIAL_DERIVED_VERIFIED`, `REFERENCE_VERIFIED`, `MAPPING_ONLY`, `EXTRACTION_REQUIRED`, `FUTURE_SCOPE`, and `UNSUPPORTED` have exact evidence criteria.

## 51. Phase 11-5 Closure Criteria
Reference, golden benchmark, tolerance, variance, Tool/input/example coverage, reproducibility, limitations, manifest, and acceptance deliverables are mandatory.

## 52. Phase 12 UI/UX Scope Seal
Phase 12 covers IA/design system/navigation/Planner/Workspace/viewers/findings/Inspector/Report/Recipe/responsive/accessibility only; new scientific authority defaults to zero.

## 53. Phase 13 Final Product Closure Scope Seal
Phase 13 covers fact alignment, integration gaps, seven E2E demos, docs/reproducibility, polish, regression, and archive/presentation.

## 54. Future Scope Guard
Fermi surface, projected bands, Rietveld, DFT/GW, Bader, defects/surfaces, advanced transport/trajectory science, and arbitrary Python remain unqueued.

## 55. Not Planned Guard
Generic workflow/DAG/notebook/replanning/RAG/plugins/SaaS/billing/enterprise/Kubernetes/distributed scheduler/KMS and unrestricted providers remain excluded.

## 56. Canonical Authority Order
Goal/requirements -> ROADMAP -> persistent state -> TASKS -> reviewer prompt -> generated next-scope suggestion.

## 57. Acceptance Registry
P11V0-A01 through P11V0-A10: expected/implemented 10/10; missing/extra/duplicate/conflicting/shorthand 0.

## 58. Evidence Inventory
Structured Registry, Artifact, input, parser, evidence, reference, fixture, official-example, tolerance, variance, gaps, levels, triggers, acceptance, and roadmap files are retained.

## 59. Evidence Manifest
Normalized manifest has entries >0, missing/hash/secret-bearing evidence 0; docs links and Phase 11 secret-pattern checks pass.

## 60. Documentation Changes
Phase 11 governance documents, ROADMAP, docs index, README, and shared-schema evidence-only boundary were updated.

## 61. Persistent State Changes
PROJECT_BRIEF, DESIGN_PROGRESS, TASK_BOARD, CHANGELOG, OPEN_QUESTIONS, ADRs, and Registry notes record Phase 10N completion and the new route.

## 62. Security
No arbitrary code/scientific shell generation/notebook/downloaded script/external scientific API/reference download/frontend recomputation/LLM authority; secret-pattern scan passed.

## 63. LLM / DeepSeek
`NEW_LLM_CALL_SITES = 0`; `PHASE11_0_REQUIRES_LLM = NO`; `REAL_LLM_CALLS = 0`; existing DeepSeek-only policy regressed only.

## 64. Database / API / Dependency Freeze
Database schema, migration 0007, public API family, dependencies, lockfile, Registry, and DataProfile are unchanged.

## 65. Tests
Local: backend 1263 passed; frontend 449 passed; typecheck/build/lock/diff/evidence passed. CI `31324356338` passed Unit, Frontend/browser/build, and service-backed jobs.

## 66. Browser Regression
Exact-SHA CI Frontend/browser replay job passed Chromium, Firefox, WebKit, and mobile retained matrix.

## 67. Service-Backed Regression
Exact-SHA CI PostgreSQL/Redis/MinIO job passed with its zero-skip gate.

## 68. npm Audit Status
`npm audit = UNAVAILABLE`; configured mirror returned `404_NOT_IMPLEMENTED`. Dependency lock consistency and security tests passed.

## 69. Files Changed
Docs, persistent state, evidence, one deterministic audit generator, and audit/TASKS compatibility tests only; production source changes 0.

## 70. Commit / CI History
Implementation `312fd4445d404f0f89c061fbdc055789912dc552` / CI `31324356338`: success. Completion record: this commit. Per explicit user direction, later documentation/queue commits are submitted without waiting for additional CI.

## 71. Queue State
At completion-record creation, exactly one completed Phase 11-0 task remains pending queue archive.

## 72. Automatic 11-1 Entry
`PHASE_11_1_EXECUTABLE_TASK_CREATED = NO`; Phase 11-1 remains reviewer-gated.

## 73. Final Repository State
Registry 62, DataProfile 2.4, migration 0007, master. Queue archive follows as a separate direct commit; Phase 12/13 remain approved roadmap only.

## 74. Reviewer Decision Required for 11-1
Phase 11-1 requires a new reviewer prompt before any reference acquisition, extraction, fixture consolidation, or task admission.

Mandatory markers: `PHASE11_0_NEW_SCIENTIFIC_TOOLS = 0`; `PHASE11_0_NEW_SCIENTIFIC_ALGORITHMS = 0`; `PHASE11_0_NEW_ARTIFACT_FAMILIES = 0`; `PHASE11_0_NEW_DATAPROFILE_VERSION = 0`; `PHASE11_0_NEW_ANALYSISPLAN_VERSION = 0`; `PHASE11_0_NEW_PUBLIC_API_FAMILIES = 0`; `PHASE11_0_NEW_DATABASE_MIGRATIONS = 0`; `PHASE11_0_NEW_DEPENDENCIES = 0`; `PHASE11_0_NEW_LLM_CALL_SITES = 0`; `PHASE11_0_REAL_LLM_CALLS = 0`; `PHASE11_0_EXTERNAL_REFERENCE_DOWNLOADS = 0`; `PHASE11_0_NOTEBOOK_EXECUTIONS = 0`; `PHASE11_0_DOWNLOADED_SCRIPT_EXECUTIONS = 0`.

Honesty markers: `BROWSER_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO`; `SERVICE_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO`; `FIXTURE_EXISTS_EQUALS_REFERENCE_VERIFIED = NO`; `MAPPING_EQUALS_VERIFIED = NO`; `SELF_REFERENCE_EQUALS_INDEPENDENT_REFERENCE = NO`; `LATEST_EVIDENCE_WINS_AUTHORITY = NO`; `GLOBAL_SCIENTIFIC_EPSILON = NONE`; `PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED`.

Roadmap markers: `PHASE_11 = SCIENTIFIC_VALIDATION`; `PHASE_12 = COMPREHENSIVE_UI_UX_PRODUCT_EXPERIENCE_REDESIGN`; `PHASE_13 = FINAL_PRODUCT_CLOSURE`; `OLD_PHASE12_FINAL_CLOSURE_NUMBERING = SUPERSEDED`; `FUTURE_SCOPE = DOCUMENTED_NOT_QUEUED`; `PHASE14 = NOT_CREATED`.

Queue archive addendum: completion record `dee197d39e194277351a34fcd063b3de97729534`; queue archive = this commit. `TASK_BLOCK_COUNT = 0`; Phase 11-1 remains `REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 12/13 are roadmap-approved, not queued, and not executable. The implementation CI is the sole waited/verified CI per explicit user direction.

# Phase 11-1 Reference Provenance + Safe Fixture Consolidation Result

## 1. Conclusion
Reference and fixture inputs required for the approved Phase 11-2 benchmark scope are provenance-sealed and safely prepared. Scientific Tools are not declared validated in this phase.

## 2. Phase 11-0 Baseline
Entry authority is `ef40ade537820e88bbe2d259a9b4ccb9cd04ac1c`; Registry 62, DataProfile 2.4, migration 0007, and a clean queue baseline were verified.

## 3. Entry Gate
`PHASE_11_1_ENTRY_GATE = PASS`; the first task was admitted as the only active task.

## 4. Phase 11-0 Backlog Reconciliation
All 12 retained gap records were reconciled without downgrading priorities or changing scientific semantics. Actual retained counts are 46 reference-like, 170 fixtures, and 55 official/example records.

## 5. Production Behavior Changes
None. No production scientific source was changed.

## 6-15. Reference Acquisition, Version, Checksums, Retention, License
No external reference download was required. Existing repository evidence was reused with SHA-256 source identity, retained-evidence version pinning, raw-retention disposition, and explicit license/redistribution status. Official-example records remain reference-only where redistribution is unclear.

## 16-20. License Review, Reuse, Deduplication, Independence
Same checksums are classified as reused, not independent evidence. Same-library expected data is `SELF_REFERENCE`; official/example provenance with unresolved licensing is `UNRESOLVED`. No filename or recency authority is used.

## 21-30. Fixture Reuse, Identity, Checksums, Transformations
170 retained fixture records are reused without in-place rewrite. Twelve benchmark handoff views have distinct fixture identities and link back to retained source bytes. `P11TRANS-IDENTITY-001@1.0.0` is metadata-only, deterministic, and has `numericMutation=false`, `unitMutation=false`, and `orderingMutation=false`.

## 31-36. Capability Reference Preparation
N1 coordination, N2 geometry, N3 XRD, N4 trajectory, N5 electronic, phonon, volumetric, ML/composition, and earlier retained evidence are linked to typed provenance records. No numeric comparison was executed.

## 37. Official Example Reconciliation
55 official/example records remain retained historical mapping or reference-only evidence. `OFFICIAL_EXAMPLE_EXISTS != REFERENCE_VERIFIED`.

## 38. Input Support Non-Change Verification
Input verdicts are unchanged: CSV/CIF/POSCAR direct supported; canonical JSON, XYZ/EXTXYZ, volumetric, ZIP, and supplied electronic JSON supported with limits; phonon mapping-only; XLSX, Parquet, and LAMMPS trajectory unsupported.

## 39-41. Numeric, Level, and Coverage Boundaries
`PHASE11_1_NUMERIC_SCIENTIFIC_PASS_DECLARATIONS = 0`; validation-level promotions = 0; honest coverage promotions = 0. Phase 11-2 owns platform-output comparison.

## 42. Tolerance Non-Change
`TOLERANCE_CHANGES = 0`; the Phase 11-0 tolerance registry remains authoritative and pass-driven widening remains prohibited.

## 43-47. Gaps, Priorities, Unresolved Items
P0 remains 0. P1/P2 provenance, license, independent benchmark, variance, and coverage gaps remain typed in the generated unresolved matrix; no current scientific discrepancy was invented or hidden.

## 48-50. Phase 11-2 Benchmark Input Manifest
`phase11_2_benchmark_input_manifest.json` contains 12 exact handoff records, each with gap, Tool/version, reference, fixture/version/checksum, units, tolerance reference, case role, independence, readiness, and blocking reason. `IMPLEMENTATION_CRITICAL_TBD = 0`.

## 51-56. Registries and Evidence Manifest
Reference, fixture, checksum, license, raw-retention, transformation, independence, duplicate, official-example, acquisition, and benchmark manifests are under `docs/phase11/evidence/phase11_1_reference_provenance_safe_fixture/`. Manifest hashes and required-file checks passed.

## 57. Network Acquisition Audit
External downloads = 0; external scientific API calls = 0; downloaded scripts = 0; notebooks = 0; unapproved external requests = 0.

## 58-60. Security, LLM, Database/API/Dependencies
No arbitrary execution or LLM authority was added. Registry remains 62; DataProfile 2.4; migration 0007; database/API/dependencies/lockfile unchanged.

## 61. Registry / DataProfile Freeze
`REGISTRY_BEFORE_11_1 = 62`, `REGISTRY_AFTER_11_1 = 62`, `DATAPROFILE_BEFORE_11_1 = 2.4`, `DATAPROFILE_AFTER_11_1 = 2.4`.

## 62-65. Tests, Browser, Service, npm Audit
Focused governance/provenance tests passed (65 passed in the final focused set). Implementation CI `31327344030` passed Unit (1259 passed, 1 skipped), Service-backed, Frontend typecheck/build, and browser replay. Local full pytest timed out at 124 seconds without assertion output. npm audit remains subject to the repository mirror's existing unavailable policy and was not used as a PASS claim.

## 66. Files Changed
Added the Phase 11-1 evidence pack, provenance generator, tests, eight Phase 11 documents, canonical plan/lock/backlog updates, persistent state entries, and queue/result records. No production source, schema, migration, dependency, or lockfile changed.

## 67. Acceptance Registry
P11V1-A01 through P11V1-A10 are implemented exactly once; missing, extra, duplicate, conflicting, and shorthand counts are zero.

## 68-71. Commit, CI, Completion, Archive
Initial candidate `0ab99b9` failed historical queue assertions; `a9e15a3` was a fix-forward candidate with a syntax error; final implementation `cfb87369ac2af00f4a631654b841dffee8faf024` passed CI `31327344030`. Completion and queue archive are direct documentation/state commits per user instruction, with no additional CI wait.

## 72. Queue State
Phase 11-1 is completed and its block is pending archive; Phase 11-2 and Phase 11-3 remain queued in `TASKS.md` as reviewer prompts and are not executed in this task.

## 73. Phase 11-2 Gate
Phase 11-2 is reviewer-gated until a new reviewer authorization. Its benchmark inputs are prepared, but no scientific PASS is inferred.

## 74. Final Repository State
At implementation completion, `master` was pushed at `cfb87369ac2af00f4a631654b841dffee8faf024`, with Registry 62, DataProfile 2.4, migration 0007, and no production behavior change. The next queue operation is to archive only the completed Phase 11-1 block.
## Phase 11-2 Cross-Capability Golden Scientific Benchmark Suite Result

Status: PASS / COMPLETE / AWAITING VERIFIED QUEUE ARCHIVE

Phase 11-2 executed the sealed benchmark handoff from Phase 11-1 without changing production scientific authority. The implementation commit `5e2f5f07346b7c7d6b7e8d360289cce4ad95ac92` passed implementation CI `31328760532`.

### Baseline and Scope

- Phase 11-1 handoff: verified provenance, immutable fixture records, source hashes, transformation records, license dispositions, and quantity-specific tolerance ownership.
- Registry: `62` before and after. DataProfile: `2.4` before and after. Migration: `0007_phase10m1_workspace_domain` unchanged.
- Production source behavior, Registry semantics, Artifact families, DataProfile, AnalysisPlan, public APIs, dependencies, lockfile, and database schema were unchanged.
- No external reference download, notebook execution, downloaded script execution, external scientific API call, LLM call, or new scientific algorithm occurred.

### Acceptance Registry

`P11V2-A01` through `P11V2-A10` were reconciled with no missing, extra, duplicate, shorthand, or conflicting entries. The suite covers sealed handoff integrity, execution authority, expected/actual separation, invariant comparison, units and identity, positive/negative cases, Artifact/evidence integrity, honest validation-level reporting, and 11-3 handoff.

### Benchmark Outcome

The deterministic suite contains `12` benchmark records: `8` `PASS_INVARIANT`, `4` `NOT_APPLICABLE`, `0` failures, and `0` blocked cases. Aggregate status is `PASS_WITH_NONBLOCKING_LIMITATIONS`. Expected and actual records are separate, each comparison records the applicable tolerance ID and units, and every source/fixture hash is verified.

The eight passing cases validate sealed identity/unit/invariant replay through the registered-contract evidence path. Four official/reference-limited cases remain `NOT_APPLICABLE` because their retained records do not contain a bounded expected numeric value; no numeric claim is manufactured and no validation level is promoted. This is an explicit scientific limitation, not a regression failure. Phase 11-3 receives eight reproducibility-ready cases.

### Scientific Boundaries

The suite does not equate software regression with independent scientific validation. It does not treat fixture existence, mapping, screenshots, browser success, service persistence, or self-reference as independent numeric truth. It preserves algorithm-specific semantics: CrystalNN and VoronoiNN are not expected to agree; XRD correspondence is not phase confirmation; ballistic MSD is not diffusion; supplied electronic data is not platform DFT.

### Evidence and Verification

Evidence root: `docs/phase11/evidence/phase11_2_golden_scientific_benchmark/`. It contains the benchmark registry, expected/actual/comparison records, summary, manifest, discrepancy matrix, and 11-3 input handoff. Focused Phase 11 governance/provenance/benchmark tests passed: `69 passed`. Implementation CI `31328760532` passed unit tests, service-backed integration, frontend typecheck/build, and the repository browser/evidence gates.

Mandatory markers:

```text
PHASE11_2_NEW_SCIENTIFIC_TOOLS = 0
PHASE11_2_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE11_2_NEW_ARTIFACT_FAMILIES = 0
PHASE11_2_NEW_DATAPROFILE_VERSION = 0
PHASE11_2_NEW_ANALYSISPLAN_VERSION = 0
PHASE11_2_NEW_PUBLIC_API_FAMILIES = 0
PHASE11_2_NEW_DATABASE_MIGRATIONS = 0
PHASE11_2_NEW_DEPENDENCIES = 0
PHASE11_2_NEW_LLM_CALL_SITES = 0
PHASE11_2_REAL_LLM_CALLS = 0
PHASE11_2_EXTERNAL_REFERENCE_DOWNLOADS = 0
PHASE11_2_NOTEBOOK_EXECUTIONS = 0
REGISTRY_BEFORE_11_2 = 62
REGISTRY_AFTER_11_2 = 62
DATAPROFILE_BEFORE_11_2 = 2.4
DATAPROFILE_AFTER_11_2 = 2.4
```

### Queue State

Phase 11-2 is complete and awaits direct verified queue archive. Phase 11-3 remains reviewer-gated and is not executable until the next queue admission. No Phase 12 or Phase 13 task was created.
## Phase 11-3 Cross-Platform Reproducibility and Variance Characterization Result

Status: PASS / COMPLETE / AWAITING VERIFIED QUEUE ARCHIVE

Phase 11-3 used the sealed Phase 11-2 reproducibility handoff without changing production science. Corrected implementation `e89dfaf23e376a7ae79432f9806d7a4bd3eaecac` passed exact-SHA CI `31332350363` after retaining two failed historical candidates (`20fa30e`, `937b940`) and correcting only cross-platform evidence harness behavior.

### Scope and Environment

- Eight `PASS_INVARIANT` cases were admitted; the four Phase 11-2 reference-limited cases remained excluded.
- Linux `ubuntu-latest` and Windows `windows-latest` each replayed the sealed handoff under Python 3.11 and the unchanged `uv.lock`.
- The lock semantic hash canonicalizes LF/CRLF for text representation only. Fixture/resource scientific checksums remain exact.
- macOS remains `NOT_CURRENT_RELEASE_TARGET`.

### Results

Linux and Windows independently passed all eight sealed invariant reference checks. Cross-platform benchmark, reference, fixture, tolerance, and unit identities are exact; persisted invariant output hashes are exact. The input handoff contains no sealed numeric expected values, therefore numeric cross-platform comparison is `NOT_APPLICABLE` and no V4 validation level is promoted.

Browser evidence remains presentation-only across Chromium, Firefox, WebKit, and Chromium 390x844. It cannot establish numeric scientific truth and frontend scientific recomputation remains zero. PostgreSQL, Redis, and MinIO evidence remains persistence/lineage evidence rather than numeric validation.

### Evidence and Verification

Evidence root: `docs/phase11/evidence/phase11_3_cross_platform_reproducibility/`. It contains the environment, lock, identity, unit, variance, browser, limitation, security, no-mutation, and Phase 11-4 handoff records. The Phase 11-4 handoff is an input only, not a final coverage verdict.

Local verification: backend `1278 passed, 1 skipped, 49 deselected`; the skipped test is outside the required Phase 11-3 scientific matrix. Focused Phase 11 lifecycle/reproducibility tests: `74 passed`. Frontend: `449 passed`; typecheck and production build passed. CI `31332350363` passed all five required jobs: Linux replay, Windows replay, unit, service-backed integration, and frontend/browser/typecheck/build.

### Boundaries and Markers

```text
PHASE11_3_NEW_SCIENTIFIC_TOOLS = 0
PHASE11_3_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE11_3_NEW_ARTIFACT_FAMILIES = 0
PHASE11_3_NEW_DATAPROFILE_VERSION = 0
PHASE11_3_NEW_ANALYSISPLAN_VERSION = 0
PHASE11_3_NEW_PUBLIC_API_FAMILIES = 0
PHASE11_3_NEW_DATABASE_MIGRATIONS = 0
PHASE11_3_NEW_DEPENDENCIES = 0
PHASE11_3_NEW_LLM_CALL_SITES = 0
PHASE11_3_REAL_LLM_CALLS = 0
PHASE11_3_EXTERNAL_REFERENCE_DOWNLOADS = 0
PHASE11_3_EXTERNAL_SCIENTIFIC_API_CALLS = 0
PHASE11_3_SCIENTIFIC_TOLERANCE_CHANGES = 0
REGISTRY_BEFORE_11_3 = 62
REGISTRY_AFTER_11_3 = 62
DATAPROFILE_BEFORE_11_3 = 2.4
DATAPROFILE_AFTER_11_3 = 2.4
LINUX_EQUALS_SCIENTIFIC_TRUTH = NO
WINDOWS_EQUALS_SCIENTIFIC_TRUTH = NO
CROSS_PLATFORM_AGREEMENT_EQUALS_REFERENCE_PASS = NO
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
BROWSER_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
SERVICE_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

### Queue State

Phase 11-3 is complete pending direct queue archive. Phase 11-4 remains reviewer-gated, not queued, and not executable. No Phase 12 or Phase 13 task was created.

# Phase 11-4 Honest Tool / Input / Official-Example Coverage Matrix Result

## 1. Conclusion

Phase 11-4 completed the approved audit-only coverage reconciliation. The 62 live Registry Tools, 14
existing input families, and 55 retained official/example records are classified with explicit limits.
This is not Phase 11 closure; Phase 11-5 remains the reviewer-gated closure authority.

## 2. Baseline and lifecycle

Phase 11-3 verified archive authority was `70c2a46`. Implementation candidate `0d57a99` was retained as
historical failed CI candidate after run `31347561130` failed only on a CRLF/LF evidence-hash assertion.
Fix-forward implementation `09250b163cd3957815ce67238163225efc689d83` passed exact-SHA CI
`31348272583`: Linux replay PASS, Windows replay PASS, Unit PASS, service-backed PASS, and frontend
typecheck/build/browser PASS. No history was rewritten.

Entry facts: Registry `62`, DataProfile `2.4`, migration `0007_phase10m1_workspace_domain`, and no
production scientific source change. Local verification was `1282 passed, 50 skipped, 63 warnings`;
frontend was `449 passed`; typecheck, build, lock check, focused coverage tests (`4 passed`), and
queue-compatibility tests (`63 passed`) passed. The first local `uv run pytest` invocation had an existing
Windows import-collection issue; the canonical `uv run python -m pytest -q` command passed.

## 3. Coverage governance

The authoritative coverage taxonomy is `DIRECT_VERIFIED`, `OFFICIAL_DERIVED_VERIFIED`,
`REFERENCE_VERIFIED`, `MAPPING_ONLY`, `EXTRACTION_REQUIRED`, `FUTURE_SCOPE`, and `UNSUPPORTED`.
Coverage is separate from validation level, input support, browser status, service status, and
reproducibility. Browser screenshots, service persistence, fixtures, internal regression, and mapping are
not independent scientific numeric references. Self-reference is not independent cross-library evidence.

## 4. Reconciled inventory

- Tool matrix: 62 unique live Registry rows, all versions `0.1.0`, all classified `MAPPING_ONLY` for this
  coverage axis; no validation-level promotion and no V4 row.
- Input matrix: 14 rows; support verdicts unchanged. Ten input paths are `DIRECT_VERIFIED` on the
  input-path axis, one is `MAPPING_ONLY`, and three are `UNSUPPORTED`.
- Official/example matrix: 55 retained rows, all `MAPPING_ONLY`; no official-derived or independent
  scientific reference claim was added.
- Phase 11-2 reconciliation: 12 records, 8 `PASS_INVARIANT`, 4 `NOT_APPLICABLE`, 0 failures.
- Phase 11-3 reconciliation: 8 admitted cases, Linux/Windows invariant replay PASS, numeric cross-platform
  status `NOT_APPLICABLE`, V4 promotion `0`.
- Existing N1-N5 and earlier initial-release scientific capability coverage remains bounded by inherited
  Tool contracts, input support, validation level, references, tolerances, fixtures, and gap records.

## 5. Public claims and limitations

Allowed wording is limited to coverage classified from retained evidence and facts derived under the
stated contract. Do not claim all Tools are independently scientifically validated, all formats are
directly supported, all platforms have numeric reproducibility, or that mapping/fixtures/screenshots prove
scientific correctness. The complete public claim matrix, known limitations, support matrix, and remaining
gaps are in `docs/phase11/` and the Phase 11-4 evidence directory.

## 6. Handoff and freeze

The exact machine-readable handoff is
`docs/phase11/evidence/phase11_4_honest_tool_input_example_coverage/phase11_5_closure_input_manifest.json`.
It records zero P0 gaps, zero numeric cross-platform claims, zero V4 promotions, no reference/fixture/
expected-value/tolerance mutation, and no production authority change. Phase 11-1 through 11-5 scope,
Future Scope, Not Planned boundaries, security, LLM, dependency, migration, and lockfile policies remain
unchanged.

## 7. Mandatory markers

```text
PHASE11_4_NEW_SCIENTIFIC_TOOLS = 0
PHASE11_4_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE11_4_NEW_ARTIFACT_FAMILIES = 0
PHASE11_4_NEW_DATAPROFILE_VERSION = 0
PHASE11_4_NEW_ANALYSISPLAN_VERSION = 0
PHASE11_4_NEW_DATABASE_MIGRATIONS = 0
PHASE11_4_NEW_PUBLIC_API_FAMILIES = 0
PHASE11_4_NEW_DEPENDENCIES = 0
PHASE11_4_NEW_LLM_CALL_SITES = 0
PHASE11_4_REAL_LLM_CALLS = 0
PHASE11_4_EXTERNAL_REFERENCE_DOWNLOADS = 0
PHASE11_4_EXTERNAL_SCIENTIFIC_API_CALLS = 0
PHASE11_4_NEW_SCIENTIFIC_BENCHMARKS = 0
PHASE11_4_VALIDATION_LEVEL_PROMOTIONS = 0
PHASE11_4_VALIDATION_LEVEL_DEMOTIONS = 0
PHASE11_4_REFERENCE_MUTATIONS = 0
PHASE11_4_FIXTURE_MUTATIONS = 0
PHASE11_4_EXPECTED_VALUE_MUTATIONS = 0
PHASE11_4_TOLERANCE_CHANGES = 0
REGISTRY_BEFORE_11_4 = 62
REGISTRY_AFTER_11_4 = 62
DATAPROFILE_BEFORE_11_4 = 2.4
DATAPROFILE_AFTER_11_4 = 2.4
MIGRATION_AFTER_11_4 = 0007_phase10m1_workspace_domain
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

## 8. Queue state

Phase 11-4 is `PASS / HONEST_COVERAGE_SEALED / QUEUE_ARCHIVED` after the direct completion and archive
commits. Phase 11 remains `IN_PROGRESS / SCIENTIFIC_VALIDATION_AND_COVERAGE_COMPLETE / AWAITING_FINAL_CLOSURE`.
Phase 11-5 is `REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 12 and Phase 13 are approved, not queued,
and not executable. No automatic Phase 14 exists.

# Phase 11-5 Scientific Validation Closure + Release Candidate Gate Result

## Conclusion

Phase 11 is `COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS` and
`SCIENTIFIC_VALIDATION_RELEASE_CANDIDATE = PASS`. This is a sealed validation
baseline, not an assertion that every scientific value is independently validated
or that the final product is release-ready. `INITIAL_RELEASE_COMPLETE = NO` and
`FINAL_PRODUCT_RELEASE_READY = NO`.

## Closure

- Reconciled Phase 11-0 governance, Phase 11-1 provenance/fixture records,
  Phase 11-2 golden benchmarks, Phase 11-3 Linux/Windows replay, and Phase
  11-4 honest coverage without creating a new scientific authority.
- Preserved 62 Registry Tools, DataProfile 2.4, AnalysisPlan 0.1/0.2,
  migration `0007_phase10m1_workspace_domain`, dependencies, lockfile, APIs,
  scientific contracts, reference records, fixtures, expected values,
  tolerances, and validation levels.
- Sealed the final reference, fixture, golden benchmark, tolerance, variance,
  reproducibility, limitation, evidence-index, and Phase 12 read-only handoff
  packages under `docs/phase11/` and the Phase 11-5 evidence manifest.
- Retained the bounded evidence verdicts: 12 golden records with 8 invariant
  passes, 4 explicit reference-limited N/A cases, and 0 failures; eight
  Linux/Windows invariant replays, numeric cross-platform `NOT_APPLICABLE`, and
  V4 promotion 0; 62 Tool, 14 input, and 55 example coverage rows.

## CI And Regression

Implementation `953866ef524a7f60532d5d6326e2049b4e7d2bc0` passed exact-SHA CI
`31351418205`: Unit, PostgreSQL/Redis/MinIO service integration, Linux and
Windows replay, frontend typecheck/build, and the browser replay matrix all
passed. The lifecycle regression fix explicitly allows an empty `TASKS.md` only
after all task blocks are archived; tasks that remain still require `处理中`.

Local verification: `uv lock --check`; `uv run python -m pytest -q`
(`1287 passed, 50 skipped`); `npm --prefix apps/web test` (`449 passed`);
`npm --prefix apps/web run typecheck`; `npm --prefix apps/web run build`; focused
Phase 11-4/11-5 evidence tests (`9 passed`); generator, manifest, and
`git diff --check` all passed. The existing Plotly/glslify build warnings remain
non-fatal. `npm audit` remains unavailable because the configured mirror returns
`404_NOT_IMPLEMENTED`.

## Acceptance And Limits

`P11V5-A01` through `P11V5-A12`: expected 12, implemented 12,
missing/extra/duplicate/conflicting/shorthand 0. Reference-limited numeric cases
remain N/A; mapping-only coverage remains disclosed; input-path support remains
separate from numeric validation; screenshots, browser and service success are
not numeric reference authority; universal cross-platform numeric equivalence is
not claimed. Future Scope and Not Planned boundaries are unchanged.

## Mandatory Markers

```text
PHASE11_5_NEW_SCIENTIFIC_TOOLS = 0
PHASE11_5_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE11_5_NEW_SCIENTIFIC_BENCHMARKS = 0
PHASE11_5_NEW_REFERENCE_SOURCES = 0
PHASE11_5_NEW_CROSS_PLATFORM_CASES = 0
PHASE11_5_NEW_ARTIFACT_FAMILIES = 0
PHASE11_5_NEW_DATAPROFILE_VERSION = 0
PHASE11_5_NEW_ANALYSISPLAN_VERSION = 0
PHASE11_5_NEW_DATABASE_MIGRATIONS = 0
PHASE11_5_NEW_PUBLIC_API_FAMILIES = 0
PHASE11_5_NEW_DEPENDENCIES = 0
PHASE11_5_NEW_LLM_CALL_SITES = 0
PHASE11_5_REAL_LLM_CALLS = 0
PHASE11_5_EXTERNAL_REFERENCE_DOWNLOADS = 0
PHASE11_5_EXTERNAL_SCIENTIFIC_API_CALLS = 0
PHASE11_5_VALIDATION_LEVEL_CHANGES = 0
PHASE11_5_TOOL_COVERAGE_CHANGES = 0
PHASE11_5_INPUT_SUPPORT_CHANGES = 0
PHASE11_5_EXAMPLE_COVERAGE_CHANGES = 0
PHASE11_5_REFERENCE_MUTATIONS = 0
REGISTRY_BEFORE_11_5 = 62
REGISTRY_AFTER_11_5 = 62
DATAPROFILE_BEFORE_11_5 = 2.4
DATAPROFILE_AFTER_11_5 = 2.4
MIGRATION_AFTER_11_5 = 0007_phase10m1_workspace_domain
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
BROWSER_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO
SERVICE_PASS_EQUALS_NUMERIC_REFERENCE_PASS = NO
PASS_DRIVEN_TOLERANCE_CHANGE = PROHIBITED
```

## Queue State

Phase 11-5 is `PASS / ARCHIVED_BY_VERIFIED_QUEUE_COMMIT` at
`a15bf2b1913e001cc6ed7423c3f9cba295147395`; the completion record is
`5b5555de25e68780c8e0f696e12b604d0e633365`. Phase 11 is
`COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS`. Phase 12 is
`REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 13 is
`ROADMAP_APPROVED / NOT_QUEUED / NOT_EXECUTABLE`; Phase 14 is not created.

# Phase 12-0 Current UX Reality Audit + Product Experience Seal Result

## 1. Conclusion

Phase 12-0 is `PASS / PRODUCT_EXPERIENCE_AUDITED / EXPERIENCE_SEAL_PROPOSED`.
The current product was inventoried and audited across routes, user-visible
surfaces, components, journeys, scientific viewers, states, terminology,
responsive behavior, accessibility, and evidence boundaries. This result does
not mean the UI was redesigned or that the product is release-ready.

## 2. Phase 11 Baseline

Phase 11 is `COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS` and remains the
read-only scientific authority. Its sealed baseline is `5273b5e...`; the Phase
11-5 implementation `953866ef524a7f60532d5d6326e2049b4e7d2bc0` passed CI
`31351418205`. Registry 62, DataProfile 2.4, AnalysisPlan 0.1/0.2, and migration
`0007_phase10m1_workspace_domain` were preserved.

## 3. Entry Gate

Entry was verified at `8903e045cbad86ba0333ca4d009997e5132f73bc`, with matching
`origin/master`, branch `master`, clean worktree, empty queue, no Phase 12-1 or
Phase 13 task, and no production change authority. The Phase 11 authority handoff,
coverage/limitations records, and browser/service evidence roots resolved.

## 4. Repository State

The implementation commit is `0ea893bb85d6abd90ab89bc81e1606b378ea1e7f`.
The audit-only change set contains documentation, deterministic evidence tooling,
tests, persistent state, and queue metadata. Production React, CSS, backend
behavior, APIs, schemas, scientific contracts, Registry, Profile, dependencies
and lockfile are unchanged.

## 5. Production Behavior Changes

None. `PHASE12_0_PRODUCTION_UI_CHANGES = 0`,
`PHASE12_0_PRODUCTION_BEHAVIOR_CHANGES = 0`, and
`PHASE12_0_SCIENTIFIC_BEHAVIOR_CHANGES = 0`.

## 6. Scientific Authority Handoff

Phase 11 coverage, public claims, limitations, validation levels and reference
status are indexed read-only. UI labels, screenshots, service evidence and UX
matrices cannot upgrade `MAPPING_ONLY`, `NOT_APPLICABLE`, or reference-limited
records.

## 7. Phase 11 Coverage/Limit Reconciliation

The snapshot records 12 golden records, 8 invariant passes, 4 explicit N/A cases,
0 scientific failures, Linux and Windows invariant replay PASS, numeric
cross-platform validation NOT_APPLICABLE, and V4 promotions 0.

## 8. Current Route Inventory

The live source audit records `/`, `/workspaces/{workspaceId}`, loading and error
boundaries, and route-derived navigation surfaces in
`docs/phase12/evidence/phase12_0_current_ux_reality/route_inventory.json`.

## 9. UI Surface Registry

The surface registry contains 27 specialized surfaces plus route boundaries,
including Planner, upload/setup, Profile, execution, Workspace, findings,
evidence, Inspector, provenance, Report, Recipe, settings, and explicit loading,
empty, unsupported, stale and error states. `UI_SURFACE_UNCLASSIFIED = 0`.

## 10. Component Inventory

Frontend source scanning classified navigation, shell, controls, tabs, panels,
tables, charts, 3D, timeline, dialogs, drawers, status, Inspector, Evidence,
Report, Recipe, Settings and developer/audit components. `UI_COMPONENT_UNCLASSIFIED = 0`.

## 11. Current Design-System Audit

The audit records the live stylesheet and component vocabulary, including CSS
variables, hard-coded values, typography, spacing, borders, surfaces, focus,
motion, breakpoints and density. It is a reality baseline for 12-1, not a token
rewrite.

## 12. Token/Visual Vocabulary Audit

Token counts and duplicate visual patterns are captured in
`design_token_inventory.json` and `component_consistency_matrix.json`. The
result identifies uncontrolled vocabulary and duplicated viewer chrome without
changing CSS.

## 13. Information Hierarchy Audit

The current hierarchy is artifact- and implementation-aware. The sealed target
is result-first presentation with progressive disclosure: meaning and limitations
first, then scientific details, then provenance/developer detail.

## 14. Global Navigation Audit

The audit covers current navigation entry/exit and records the candidate IA
`Home / Data / Analyses / Workspaces / Reports / Settings` as ACCEPTED for 12-1
implementation review, preserving the existing URL and server authority.

## 15. Planner/Agent UX Audit

Planner context, prompt, intent, clarification, eligibility, plan and execution
surfaces are indexed. The primary friction is internal planning concepts exposed
too early; the target is a human-readable plan before developer details.

## 16. Data/Profile UX

Data selection and Profile readiness are audited as context for analysis. Profile
facts remain backend authority and are not recomputed or inferred by the UI.

## 17. Prompt Composer UX

Selection context, examples, input affordance, disabled/loading/error states and
mobile input behavior are covered by the Planner audit and journey evidence.

## 18. Clarification UX

Clarification is audited for human-readable rationale, valid choices, context
preservation, keyboard behavior, and leakage of raw schema/internal IDs.

## 19. Eligibility UX

Capability availability is audited as an Eligibility-derived state. Unsupported
and mismatched capabilities remain explicit; the UI cannot select a Tool from
keywords alone.

## 20. Plan UX

Plan presentation is classified into human approach first and developer detail
second. Exact Tool, Artifact, dependency and contract information remains available
through the audit/provenance layer.

## 21. Execution/Timeline UX

The audit maps existing runtime states to understandable progress language without
inventing backend states: preparing, planning, validating, queued, running,
producing results, interpreting, workspace construction, complete, partial and
failed.

## 22. Planner-to-Workspace Transition

The transition preserves one Workspace per Job and exact URL/server authority;
Phase 12-2 owns presentation improvements only.

## 23. Workspace Shell UX

Header, context rail, active panel, gallery, viewer, Inspector, findings, evidence,
report, history, save and recovery are in `workspace_audit.json`.

## 24. Workspace Navigation UX

The target Workspace IA is ACCEPTED for reviewer-gated implementation:
`Overview / Data / Analysis / Results / Findings / Evidence / Report`, with
`Provenance / Developer Details` subordinate. One active panel remains the rule.

## 25. Artifact Gallery UX

Gallery and artifact-centric navigation are audited as provenance surfaces. The
target is to present scientific result summaries first while retaining exact
Artifact identity and checksum details.

## 26. Scientific Result UX

`RESULT_FIRST_UI = YES`. Result cards expose type, summary, status, warnings and
next action; Artifact and ToolCall are deeper audit details, never removed.

## 27. Viewer Inventory

The viewer matrix covers Dataset Explorer, ML, Composition Space, Structure,
Coordination, Local Environment, XRD, Trajectory, RDF/MSD/Diffusion, Phonon/BZ,
Volumetric, Electronic Band and DOS surfaces.

## 28. Chart Viewer UX

Chart controls, legend, selection, tooltip, table alternative, export and loading
states are inventoried. 12-3 owns unified chart chrome; plots remain presentation
only.

## 29. 3D Viewer UX

Camera, cell, axes, labels, selection, fullscreen, snapshot and animation controls
are inventoried. `WEBGL_PRESENTATION_ONLY = YES`; numeric values remain Artifact
authority.

## 30. Dataset Explorer UX

Dataset context, loading, empty, ready and navigation states are included in the
surface and journey registries.

## 31. Materials ML UX

Materials ML is included in the viewer and scientific-result audit; metric/table
authority remains persisted output and the UI performs no PCA/KMeans recomputation.

## 32. Composition Space UX

Composition-space visualization and table alternatives are inventoried as data
intelligence/presentation surfaces with exact source context retained.

## 33. Structure UX

Structure summary and 3D presentation are included, with site identity and
geometry remaining backend/Artifact authority.

## 34. Coordination UX

CrystalNN and VoronoiNN are represented as separate result authorities; the audit
does not merge or rank their scientific results.

## 35. Local Environment/Polyhedra UX

Local environment, polyhedron, periodic-site and selection presentation are
covered; N1 dependency and exact identity remain unchanged.

## 36. Experimental XRD UX

Peak matching, residuals, matched/unmatched states, warnings and limitations are
audited. Peak correspondence is not presented as phase confirmation.

## 37. Trajectory UX

Trajectory context, frame/atom/time/cell semantics, heavy payload loading and
selection are included in the viewer matrix.

## 38. RDF/MSD/Diffusion UX

RDF, MSD and diffusion panels are audited for diagnostics, fit-window disclosure,
ballistic rejection and missing-time limits. The UI never recomputes or silently
fits scientific data.

## 39. Phonon/BZ UX

Phonon band/DOS combined and Brillouin Zone surfaces are inventoried with chart
and 3D presentation boundaries.

## 40. Volumetric UX

Volumetric fields, slices, isosurfaces and volume-rendering surfaces are included;
rendered views are not scientific numeric authority.

## 41. Band Structure/DOS UX

Band/DOS surfaces preserve supplied-data wording, gap/fermi/spin/projection
limitations, numeric alternatives and compatibility boundaries.

## 42. Findings UX

Finding visibility, claim hierarchy, confidence semantics, warnings, limitations
and result/evidence relationships are audited.

## 43. Evidence UX

The target trust path is `Finding -> Evidence -> Artifact -> Tool/version -> input
identity -> provenance`; screenshots and browser results remain UX evidence only.

## 44. Inspector UX

The sealed target is a three-layer Inspector: Summary, Scientific Details,
Provenance. Developer details remain accessible but subordinate.

## 45. Provenance UX

Source identity, hashes, Tool/version, parameters, units, coverage, limitations
and lineage remain discoverable through provenance surfaces.

## 46. Warning/Limitation UX

Warnings and scientific limitations must be visible near results and understandable,
not hidden in raw JSON. Phase 11 public claim/limitation records are the authority.

## 47. Report UX

Report source discovery, composition, ordering, captions, warnings, preview,
finalization, history and export are inventoried; reports compose persisted facts.

## 48. Recipe UX

Recipe is targeted to a human-readable reproducibility explanation with exact raw
declaration available. `RECIPE_EXECUTION_AUTHORITY = NONE` remains permanent.

## 49. Save/Reload/Recovery UX

Workspace history, save/reload, stale state, revision conflict, recovery and
selection restoration are represented in the error/recovery and journey matrices.

## 50. Error UX

Validation, unsupported, mismatch, provider, plan, runtime, dependency, Artifact,
Workspace, revision, Report and cross-project errors are covered with context-
preserving recovery ownership.

## 51. Empty-State UX

No-data, no-analysis, no-Workspace, no-result, no-finding, no-evidence, no-report,
unsupported, not-run and no-match states are classified for explanation and action.

## 52. Loading UX

Initial, Profile, planning, execution, Artifact, heavy viewer, interpretation and
Report loading states are catalogued, including cancellation and progress needs.

## 53. Status Vocabulary

Current status strings are indexed for duplicate meanings, technical leakage,
capitalization drift and bilingual consistency.

## 54. Terminology/i18n

The audit distinguishes fully localized, partial, English-only, developer-only,
inconsistent and not-applicable vocabulary. No new i18n infrastructure was added.

## 55. Provider/Settings UX

Current provider and secret-handling policy was audited from repository authority;
no frontend secret leakage or provider policy change is proposed.

## 56. Accessibility

Keyboard, focus, semantics, status announcements, table/chart/3D alternatives,
reduced motion, contrast, zoom and touch targets are covered. The target is
WCAG-like AA as an engineering goal, not certification.

## 57. Responsive/Desktop

Desktop and mobile evidence infrastructure is indexed for 1440x900, 1280x720 and
390x844 where available. Mobile shares authority with desktop while changing layout.

## 58. Mobile 390x844

The canonical mobile audit preserves one active panel, context/navigation drawer,
panel switcher and Inspector bottom-sheet patterns; it does not redesign production.

## 59. 200% Zoom

Planner, Workspace, Results, Findings and Report reflow/overflow checks are part of
the accessibility backlog and evidence contract.

## 60. Reduced Motion

Reduced-motion behavior is inventoried as a Phase 12-6 requirement; no runtime
animation behavior was changed by 12-0.

## 61. Browser Matrix

The implementation CI replayed Chromium, Firefox, WebKit and 390x844 coverage.
Browser PASS is presentation/interaction evidence and not numeric science evidence.

## 62. Canonical User Journeys

Eleven journeys cover new data, natural-language analysis, professional analysis,
result understanding, Report, historical recovery, unsupported input, partial
execution, provider setup, mobile inspection and developer provenance.

## 63. Interaction Baseline

Route/panel transitions, click/keyboard proxies, scroll and internal-identifier
visibility are recorded as automated interaction proxies, not human usability study
claims.

## 64. UX Problem Matrix

Ten problems are captured with evidence, consequence, viewport/input scope,
acceptance method and owner. `UX_PROBLEM_UNASSIGNED = 0`.

## 65. P0/P1/P2/P3 Distribution

Distribution is P0=0, P1=6, P2=4, P3=0. P1/P2 findings are backlog work, not
12-0 blockers; no P0 scientific misrepresentation was found by this audit.

## 66. Product Experience Principles

Sealed principles are meaning before mechanism, result before Artifact, progressive
disclosure, first-class limitations, one primary action, non-color state, exact
identity availability, shared authority across viewports, lazy heavy viewers,
context-preserving errors, subordinate developer detail and no UX-created science.

## 67. Information Architecture Decision

Global IA candidate `Home / Data / Analyses / Workspaces / Reports / Settings` and
Workspace IA `Overview / Data / Analysis / Results / Findings / Evidence / Report`
with `Provenance / Developer Details` were accepted as reviewer-gated targets.

## 68. Experience Decision Registry

P12-D001 through P12-D020 are recorded, including visual direction, disclosure,
result-first hierarchy, limitations, IA, viewer chrome, Inspector, Recipe,
terminology, accessibility, evidence methodology and phase ordering.

## 69. Phase 12-1 Handoff

12-1 receives the live token/component inventory, consistency gaps, accessibility
gaps, semantic status requirements, scientific hierarchy rules, density rules and
responsive constraints.

## 70. Phase 12-1--12-7 Backlog

The implementation backlog assigns goals, source areas, allowed/forbidden changes,
acceptance IDs, browser/mobile/accessibility/scientific-authority/evidence gates
and exit criteria to 12-1 through 12-7.

## 71. Acceptance Plan

P12X0-A01 through P12X0-A12 are implemented with no missing, extra, duplicate,
conflicting or shorthand entries. Each future subphase has eight unique acceptance
IDs, 56 total, consistently repeated in backlog, plan, lock and manifest.

## 72. Execution Lock

Phase 12 may redesign presentation, interaction, hierarchy and product experience
only after reviewer approval. Registry, Profile, Intent, Eligibility, Plan,
Validator, Runtime, Artifact, Workspace identity, Selection, Report/Recipe and
Phase 11 scientific authority are locked.

## 73. Evidence Inventory

The evidence root contains deterministic route, surface, component, token,
hierarchy, journey, viewer, state, browser, accessibility, security, Phase 11
authority snapshot, decision registry, acceptance and manifest records.

## 74. Security

No arbitrary execution, external Artifact execution, frontend scientific
recomputation, scientific authority change, real LLM, external scientific API or
secret disclosure was added. Secret scan passed.

## 75. LLM / DeepSeek

`PHASE12_0_REQUIRES_LLM = NO`, `PHASE12_0_NEW_LLM_CALL_SITES = 0`, and
`PHASE12_0_REAL_LLM_CALLS = 0`. Existing provider policy is read-only.

## 76. Database/API/Dependency Freeze

New tables, columns, migrations, public API families, Python/frontend dependencies,
lockfile changes, Registry changes and DataProfile changes are all zero.

## 77. Tests

Local backend `1290 passed, 50 skipped`; frontend `449 passed`; typecheck, build,
lock check, focused audit tests, queue lifecycle tests, evidence generator,
manifest and diff checks passed. Existing build warnings are non-fatal Plotly/glslify
dynamic-require warnings.

## 78. Service-Backed Regression

The implementation CI service job passed PostgreSQL, Redis and MinIO integration,
including zero-skipped assertion. No service behavior was added.

## 79. Browser Regression

The implementation CI browser job passed the retained Chromium, Firefox, WebKit,
390x844 and professional Phase 10 replay matrix with no audit-induced production
change.

## 80. npm Audit

`npm audit = UNAVAILABLE`: the configured mirror returns `404_NOT_IMPLEMENTED`.
Lock consistency, dependency installation, frontend tests, typecheck and build pass.

## 81. Files Changed

See commit `0ea893bb85d6abd90ab89bc81e1606b378ea1e7f` and the Phase 12 evidence
manifest. Changes are limited to audit tooling/tests, docs, persistent state and
queue lifecycle records.

## 82. Acceptance Registry

P12X0-A01..A12: expected 12, implemented 12, missing 0, extra 0, duplicate 0,
conflicting 0, shorthand 0.

## 83. Implementation Commit

`0ea893bb85d6abd90ab89bc81e1606b378ea1e7f`.

## 84. Implementation CI

Exact-SHA CI `31354589883` completed successfully. This is the only CI result
waited for in this phase.

## 85. Failed Candidates

No failed Phase 12-0 implementation candidate exists.

## 86. Completion Record

This result is the completion record. It is committed directly after implementation
CI success under the authorized lifecycle policy.

## 87. Queue Archive

After this completion commit, only the completed Phase 12-0 task is removed from
`TASKS.md`; no Phase 12-1 or Phase 13 task is created. The lifecycle wording is
`IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI`, `COMPLETION_RECORDED`, `QUEUE_ARCHIVED`.

## 88. Queue State

Final state: Phase 12-0 `PASS / PRODUCT_EXPERIENCE_AUDITED /
EXPERIENCE_SEAL_PROPOSED / QUEUE_ARCHIVED`; Phase 12 is
`IN_PROGRESS / UX_REALITY_AUDITED / AWAITING_DESIGN_SYSTEM_IMPLEMENTATION_APPROVAL`;
Phase 12-1 is `REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 13 is approved,
not queued and not executable; TASK_BLOCK_COUNT=0.

## 89. Phase 12-1 Reviewer Gate

Phase 12-1 remains `REVIEWER_GATE / AWAITING REVIEWER PROMPT` and
`PHASE_12_1_EXECUTABLE_TASK_CREATED = NO`.

## 90. Final Repository State

Registry=62, DataProfile=2.4, migration=`0007_phase10m1_workspace_domain`,
`PHASE14_CREATED = NO`, `PHASE12_0_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0`,
`UI_SURFACE_UNCLASSIFIED = 0`, `UI_COMPONENT_UNCLASSIFIED = 0`,
`CANONICAL_JOURNEYS_UNAUDITED = 0`, `PHASE12_IMPLEMENTATION_CRITICAL_TBD = 0`.
Phase 11 authority mutations are 0. The repository remains subject to the
reviewer gate before any 12-1 production implementation.

## Mandatory Markers

```text
PHASE12_0_PRODUCTION_UI_CHANGES = 0
PHASE12_0_PRODUCTION_BEHAVIOR_CHANGES = 0
PHASE12_0_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_0_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_0_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_0_NEW_ARTIFACT_FAMILIES = 0
PHASE12_0_NEW_DATAPROFILE_VERSION = 0
PHASE12_0_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_0_NEW_DATABASE_MIGRATIONS = 0
PHASE12_0_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_0_NEW_DEPENDENCIES = 0
PHASE12_0_NEW_LLM_CALL_SITES = 0
PHASE12_0_REAL_LLM_CALLS = 0
PHASE12_0_EXTERNAL_SCIENTIFIC_API_CALLS = 0
PHASE12_0_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
PHASE11_SCIENTIFIC_BASELINE_MUTATIONS = 0
PHASE11_TOOL_COVERAGE_MUTATIONS = 0
PHASE11_INPUT_SUPPORT_MUTATIONS = 0
PHASE11_VALIDATION_LEVEL_MUTATIONS = 0
PHASE11_LIMITATION_MUTATIONS = 0
PHASE11_PUBLIC_CLAIM_MUTATIONS = 0
UI_SURFACE_UNCLASSIFIED = 0
UI_COMPONENT_UNCLASSIFIED = 0
UX_PROBLEM_UNASSIGNED = 0
CANONICAL_JOURNEYS_UNAUDITED = 0
PHASE12_IMPLEMENTATION_CRITICAL_TBD = 0
PHASE12_1_EXECUTABLE_TASK_CREATED = NO
PHASE13_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
```

# Phase 13-1 Integration Fix-Forward #3 Result

状态：PASS / DURABLE_UPLOAD_TO_WORKER_HANDOFF_CLOSED / REAL_PROCESS_BOUNDARY_D0_PASS

完成时间：2026-08-12 10:01:40 +08:00

P13-R3-001 根因：真实 HTTP Phase2 upload 只把 normalized source exports 写入上传进程的 LocalFileArtifactStorage 与内存 DatasetRecord；Planner/Worker 重新加载的 SQL Dataset 没有 normalizedExports 等 durable references，fresh Worker 因而在首个 ToolCall 前以 `Unknown input ref: profile` 失败。

修复：复用现有 PostgreSQL `datasets.metadata_json`、`data_profiles.profile_json` 与 MinIO source payload authority，在 production upload 内完成 exact manifest/Profile/source persistence；Planner enqueue 前校验 durable root inputs，fresh Worker 只从 durable refs 重建，不使用手工 preload、runtime reparse、latest/filename/fuzzy fallback 或 Redis scientific payload。

Schema decision：`EXISTING_SCHEMA_SUFFICIENT`；migration 仍为 `0007_phase10m1_workspace_domain`。科学 Adapter、算法、单位、容差、Tool Registry、Artifact family 与 public API 未改变。

D0：真实 `/datasets/upload`、PostgreSQL、MinIO、自然语言 Intent、Eligibility、Planner、PlanValidator、Job、Redis enqueue 后销毁上传进程状态；fresh QueueWorkerRuntime exact-resolve root inputs，创建真实 ToolCall，执行 registered Adapter 并持久化首个 Artifact。missing object、hash mismatch、cross-project、stale Profile 均 typed reject。

验证：Level C `7/7` PASS；Level C2 `7/7` PASS；D0 PASS；后端 `1386 passed, 52 skipped`；前端 `456 passed`；typecheck/build/lock/diff PASS；PostgreSQL/Redis/MinIO required skips `0`；Chromium/Firefox/WebKit/390x844 PASS；Linux/Windows replay PASS；security/secret scan/manifest PASS；npm audit 因 configured mirror `NOT_IMPLEMENTED` 为 `UNAVAILABLE`。

实现候选：`5b2f62e0c9ad9861f12bdc82a4bb632f1a5eaf51`，CI `31553548486` FAILED。失败根因是 service-backed tests 全部通过后 workflow 仍要求 superseded test name；产品/D0 测试未失败。Fix-forward implementation SHA：`88103ff61584ba81a01ab0e5ebf2adbbc09275e1`，exact-SHA CI `31553972770` PASS。

Hash audit：Fact Model impact `NO`，current `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`；Scope Baseline impact `NO`，current `eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94`；determinism PASS。

```text
PHASE_13_1_FIX_FORWARD_3 = PASS
P13_R3_001 = CLOSED
REAL_UPLOAD_TO_FRESH_WORKER_D0 = PASS
UPLOAD_PROCESS_MEMORY_DEPENDENCY = 0
MANUAL_NORMALIZED_EXPORT_PRELOAD = 0
RUNTIME_REPARSE_FALLBACK = 0
FIRST_REAL_TOOLCALL_CREATED = YES
FIRST_REGISTERED_ADAPTER_EXECUTED = YES
FIRST_REAL_ARTIFACT_PERSISTED = YES
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
PHASE13_2_ATTEMPT_1 = FAILED_HISTORICAL
PHASE13_2_ATTEMPT_2 = FAILED_RERUN_HISTORICAL
PHASE13_2_ATTEMPT_3 = FAILED_RERUN_HISTORICAL
PHASE13_2_ATTEMPT_4 = REVIEWER_GATE / NOT_EXECUTED / NOT_QUEUED
PHASE13_2_ATTEMPT_4_EXECUTABLE_TASK_CREATED = NO
PHASE13_2_DEMOS_EXECUTED = 0
P13X2_ACCEPTANCE = 0/8
FIX_FORWARD_3_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```


# Phase 13-1 Zero-Gap Verification Closure Result

## 1. Conclusion

Phase 13-1 is `PASS / ZERO_GAP_VERIFICATION_CLOSED`. The corrected Phase 13-0
zero-gap conclusion was independently replayed without production or scientific
changes. Phase 13-2 demos remain unexecuted.

## 2. Entry And Authority

- Entry HEAD/origin: `7bf991c6524db0544f8e97024b6a5d30868ebaf5`.
- Phase 13-0 Fact Model: `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`.
- Corrected scope baseline: `93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627`.
- Phase 12 baseline: `29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4`.
- AnalysisIntent remains `1.0`: one clarification round, three questions, typed
  `CLARIFICATION_NOT_ALLOWED` for a second attempt.

## 3. Integration Seam Verification

The canonical matrix classifies 30 seams. Twenty-seven are `VERIFIED`; three
are `VERIFIED_WITH_EXPLICIT_LIMIT`. `GAP_FOUND=0`, `UNCLASSIFIED=0`.
Resource/Profile/Intent/Eligibility/Planner/Plan/Validator/Queue/Runtime/
Registry/Adapter/persistence/Artifact/Workspace/Interpretation/Evidence/
Provenance/Report/Recipe/recovery/isolation/security paths all resolve.

## 4. Registry And Runtime

- Registry: `62` unique versioned Tool identities.
- Runtime Adapter bindings: `51`.
- Explicit mapping-only/unavailable entries: `11`.
- Registry promotions or availability mutations: `0`.
- DataProfile `2.4`; AnalysisPlan `0.1 / 0.2`; migration
  `0007_phase10m1_workspace_domain` unchanged.

## 5. Seven-Demo Preflight

All seven canonical contracts are `READY_WITH_EXPLICIT_NONBLOCKING_LIMIT`:
Dataset Intelligence/Composition, Materials ML, Structure/coordination/local
environment/polyhedra/XRD, Trajectory/RDF/MSD/diffusion, Phonon/BZ,
Volumetric, and Electronic Band/DOS. This is contract preflight, not E2E PASS.

## 6. Fixture And Identity Integrity

All `11/11` retained fixtures exist, are retention-safe and match normalized
checksums. External downloads: `0`. Latest/fuzzy/filename/display-label/array-
position authority: `0`.

## 7. Persistence, Runtime And Security

Real PostgreSQL/Redis/MinIO, QueueWorkerRuntime, registered Adapter execution,
persisted Artifact, one Workspace per Job and persisted-fact Report/Recipe are
required for Phase 13-2. Recipe execution remains `NONE`; arbitrary code,
external Artifact execution, real LLM calls and external downloads in 13-1: `0`.

## 8. Release Gap Reconciliation

- `RELEASE_BLOCKERS = 0`
- `RELEASE_CRITICAL_INTEGRATION_GAPS = 0`
- `UNCLASSIFIED_RELEASE_GAPS = 0`
- Nonblocking limitations remain unchanged and publicly required.

## 9. Acceptance

`P13X1-A01..P13X1-A08 = 8/8 PASS`. Phase 13-2 acceptance IDs remain sealed
and unexecuted.

## 10. Tests

- Backend: `1335 passed, 50 skipped` locally; CI unit PASS.
- Frontend: `455 passed`; typecheck and production build PASS.
- Focused historical queue governance: `69 passed`.
- Phase 13-1/canonical governance: `14 passed`.
- `uv lock --check`, `git diff --check`, Linux/Windows invariant replay,
  PostgreSQL/Redis/MinIO, Chromium/Firefox/WebKit/390x844 evidence: PASS.

## 11. Commit And CI History

- Failed candidate: `800d15c0401a30507fe679dfa6dba3d539e39559`, CI
  `31459364889`; Linux checkout exposed Windows CRLF manifest byte-size drift.
- Fix-forward implementation: `d1a60955a77aec000f1e6fd630f0770db545421d`.
- Implementation exact-SHA CI: `31460352586 / success`.
- Completion terminology: `IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI` and
  `COMPLETION_RECORDED`; queue archive follows directly without a CI wait.

## 12. Mandatory Markers

```text
PHASE_13_1 = PASS
PHASE_13_1_MODE = ZERO_GAP_VERIFICATION_CLOSURE
PHASE13_1_PRODUCTION_CODE_CHANGES = 0
PHASE13_1_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE13_1_NEW_TOOLS = 0
PHASE13_1_NEW_ALGORITHMS = 0
PHASE13_1_NEW_ARTIFACT_FAMILIES = 0
PHASE13_1_NEW_DATAPROFILE_VERSION = 0
PHASE13_1_NEW_ANALYSISPLAN_VERSION = 0
PHASE13_1_NEW_MIGRATIONS = 0
PHASE13_1_NEW_PUBLIC_API_FAMILIES = 0
PHASE13_1_NEW_DEPENDENCIES = 0
PHASE13_1_NEW_LLM_CALL_SITES = 0
PHASE13_1_REAL_LLM_CALLS = 0
REGISTRY_BEFORE_13_1 = 62
REGISTRY_AFTER_13_1 = 62
DATAPROFILE_BEFORE_13_1 = 2.4
DATAPROFILE_AFTER_13_1 = 2.4
RELEASE_BLOCKERS = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
UNCLASSIFIED_RELEASE_GAPS = 0
INTEGRATION_SEAMS = 30/30 CLASSIFIED
DEMO_PREFLIGHT = 7/7 READY_WITH_EXPLICIT_NONBLOCKING_LIMIT
FIXTURE_INTEGRITY = 11/11 PASS
P13X1_ACCEPTANCE = 8/8
HANDCRAFTED_PLAN_INJECTION = 0
HANDCRAFTED_JOB_INJECTION = 0
HANDCRAFTED_ARTIFACT_INJECTION = 0
HANDCRAFTED_WORKSPACE_INJECTION = 0
HANDCRAFTED_REPORT_INJECTION = 0
PHASE13_2_DEMOS_EXECUTED = 0
PHASE13_2_DEMO_PASS_CLAIMS = 0
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 12-1 Design System 2.0 + Visual Language Result

## Conclusion
`PASS / DESIGN_SYSTEM_2_0_IMPLEMENTED / VISUAL_LANGUAGE_FOUNDATION_SEALED / QUEUE_ARCHIVED`.
This is presentation-only foundation work; Phase 12 and product release are not complete.

## Baselines and Authority
Phase 12-0 archive `d48ac5d28c53734d5f14f5e5728984f9ec4c2034` and implementation
`0ea893bb85d6abd90ab89bc81e1606b378ea1e7f` / CI `31354589883` are verified
ancestors. Entry was clean `master`, Registry 62, DataProfile 2.4, migration
`0007_phase10m1_workspace_domain`. Phase 11 remains read-only scientific authority:
12 golden records, 8 PASS_INVARIANT, 4 NOT_APPLICABLE, 0 scientific failures,
Linux/Windows invariant replay PASS, numeric cross-platform validation N/A, V4=0.

## Design System and UX Closure
DS2 version is 2.0. The implementation adds primitive/semantic tokens,
typography and density, surface/border/elevation, z-index, motion and reduced
motion, focus-visible, form/button/table/dialog primitives, and presentation-only
`StatusLabel`. Existing infrastructure was reused; no new route, framework, font,
external asset or scientific viewer semantics were added. The deterministic
evidence root is `docs/phase12/evidence/phase12_1_design_system_2_0/` and contains
the token, component, status, accessibility, browser, handoff, security and
no-change records. Semantic hash:
`2a87269216cddb1193af9a08ae7b136889ba43905532e508042b78369a68714d`.

`UX-007` is `FIXED_WITH_EVIDENCE`. Other owners remain open and visible:
12-2=2, 12-3=2, 12-4=1, 12-5=1, 12-6=2, 12-7=1. No new P0/P1 was introduced.
Global IA, Workspace IA, Planner workflow, scientific values, identity,
selection, backend, API, schema, Registry and DataProfile are unchanged.

## Acceptance and Verification
P12X1-A01 through P12X1-A08 were preserved from the canonical plan and pass 8/8:
tokens; typography/spacing/density; surfaces/elevation/motion; shared controls;
status/warning/limitation mapping; accessibility/focus/contrast/touch;
representative migration without IA/science change; and browser/evidence/
regression/lifecycle closure.

Local verification: backend `1293 passed, 50 skipped`, frontend `450 passed`,
typecheck PASS, build PASS, `uv lock --check` PASS, `git diff --check` PASS.
Chromium, Firefox, WebKit and Chromium 390x844 replay PASS with no console errors
or unapproved external requests. CI `31358512349` passed all five jobs:
Unit, frontend typecheck/build and retained browser replay, service-backed
PostgreSQL/Redis/MinIO, and Linux/Windows replay. `npm audit = UNAVAILABLE`
because the configured mirror returns `404_NOT_IMPLEMENTED`.

## Required Markers
```text
PHASE12_1_DESIGN_SYSTEM_VERSION = 2.0
PHASE12_1_PRODUCTION_UI_CHANGES = YES_PRESENTATION_ONLY
PHASE12_1_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_1_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_1_GLOBAL_IA_CHANGES = 0
PHASE12_1_WORKSPACE_IA_CHANGES = 0
PHASE12_1_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_1_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_1_NEW_ARTIFACT_FAMILIES = 0
PHASE12_1_NEW_DATAPROFILE_VERSION = 0
PHASE12_1_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_1_NEW_DATABASE_MIGRATIONS = 0
PHASE12_1_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_1_NEW_PYTHON_DEPENDENCIES = 0
PHASE12_1_NEW_FRONTEND_DEPENDENCIES = 0
PHASE12_1_LOCKFILE_CHANGES = 0
PHASE12_1_NEW_LLM_CALL_SITES = 0
PHASE12_1_REAL_LLM_CALLS = 0
PHASE12_1_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
DESIGN_SYSTEM_TOKEN_REGISTRY_COMPLETE = YES
UNCLASSIFIED_LEGACY_TOKENS = 0
UNCONTROLLED_HARDCODED_DESIGN_VALUES = 0
UI_COMPONENT_MIGRATION_UNCLASSIFIED = 0
UNMAPPED_USER_VISIBLE_STATUS_FAMILIES = 0
NEW_SHARED_CONTROLS_KEYBOARD_OPERABLE = PASS
NEW_SHARED_CONTROLS_FOCUS_VISIBLE = PASS
ICON_ONLY_CONTROLS_ACCESSIBLE_NAME = PASS
STATUS_COLOR_ONLY_MEANING = 0
REDUCED_MOTION_FOUNDATION = PASS
MOBILE_TOUCH_TARGET_FOUNDATION = PASS
CONTRAST_FOUNDATION = PASS
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
SUPPORTED_EQUALS_VALIDATED = NO
MAPPING_ONLY_VISUAL_UPGRADE = 0
NOT_APPLICABLE_VISUAL_UPGRADE = 0
V4_VISUAL_FABRICATION = 0
BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
REGISTRY_BEFORE_12_1 = 62
REGISTRY_AFTER_12_1 = 62
DATAPROFILE_BEFORE_12_1 = 2.4
DATAPROFILE_AFTER_12_1 = 2.4
MIGRATION_AFTER_12_1 = 0007_phase10m1_workspace_domain
PHASE12_1_OWNED_PROBLEMS = UX-007
PHASE12_1_OWNED_PROBLEM_COUNT = 1
PHASE12_1_OWNED_PROBLEMS_CLOSED = 1
PHASE12_1_OWNED_PROBLEMS_OPEN = 0
NEW_P0_INTRODUCED_BY_12_1 = 0
P12X1_ACCEPTANCE = 8/8
```

## Lifecycle, Handoffs and Final State
Implementation commit `60269556f70f07014224a801150f214887a56ee5` was verified by
exact-SHA CI `31358512349`. Completion record was committed directly after that
single CI confirmation, then only the Phase 12-1 task was archived directly;
completion/archive CI was not awaited. `COMPLETION_RECORDED = YES` and
`QUEUE_ARCHIVED = YES`. Phase 12-2 is `REVIEWER_GATE / AWAITING REVIEWER PROMPT`;
Phase 13 is approved, not queued and not executable; Phase 14 was not created.

# Phase 12-2 Global Navigation + Planner / Agent Experience Result

## Conclusion
PASS. The existing product shell now exposes the approved global IA and the
Planner explains the current journey in user language while retaining exact
developer/audit details. This is a presentation and interaction change only;
Phase 12-3 remains reviewer-gated.

## Baseline and Authority
Phase 12-1 baseline: `60269556f70f07014224a801150f214887a56ee5`, CI
`31358512349` PASS. Registry remains 62, DataProfile remains 2.4, and the
migration head remains `0007_phase10m1_workspace_domain`. Existing routes `/`
and `/workspaces/{workspaceId}` remain authoritative. Workspace, selection,
scientific artifact, Report and Recipe authorities are unchanged.

## Delivered
- Global navigation: Home, Data, Analyses, Workspaces, Reports, Settings.
- Planner stage rail: data context, intent, plan, execution, results.
- Human-readable plan approach summary before exact AnalysisPlan details.
- Four-question recovery summary: what happened, why, what can be done, and
  what was preserved.
- Deterministic route/navigation/planner/problem-closure evidence and browser
  replay for Chromium, Firefox, WebKit and Chromium 390x844.
- Legacy queue governance tests now recognize the active Phase 12-2 block and
  preserve the pending Phase 12-3 block.

## Ownership and Acceptance
`UX-001` and `UX-008` are `FIXED_WITH_EVIDENCE`. UX-002/003 remain owned by
12-3; UX-004 by 12-4; UX-005 by 12-5; UX-006/009 by 12-6; UX-010 by 12-7.
`P12X2-A01` through `P12X2-A08` are implemented: `8/8`, missing `0`, extra
`0`, duplicate `0`, conflicting `0`.

## Verification
`1296 passed, 50 skipped` backend tests; `450 passed` frontend tests;
typecheck PASS; production build PASS; `uv lock --check` PASS; `git diff
--check` PASS. Browser replay reports zero console errors, page errors,
external requests and HTTP errors in all four required contexts. Scientific
frontend recomputation is `0`; no new Tool, algorithm, Artifact family,
DataProfile, API family, database migration, dependency or LLM call site was
introduced.

## Lifecycle
Implementation commit: `d046acfcb7ea7741d7cc3567565c2cce9bcb6722`.
Implementation exact-SHA CI: `31365743510` PASS.
Completion record is committed directly after the single CI confirmation;
queue archive is committed directly without another CI wait. Phase 12-2 is
`PASS / GLOBAL_NAVIGATION_AND_PLANNER_EXPERIENCE_IMPLEMENTED / QUEUE_ARCHIVED`.
Phase 12-3 is `REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 13 is approved,
not queued and not executable.
# Phase 12-3 Scientific Workspace + Scientific Viewer Experience Result

## Conclusion
PASS. Phase 12-3 implements a result-first Scientific Workspace and shared
scientific-viewer chrome without changing scientific, Artifact, Selection,
Workspace, backend or API authority. This does not complete Phase 12.

## Baseline and Entry Gate
Phase 12-2 implementation `d046acfcb7ea7741d7cc3567565c2cce9bcb6722`
and CI `31365743510` are verified. Entry HEAD/origin was `b54e429`, branch
`master`, clean worktree, one authorized Phase 12-3 task after admission,
Registry 62, DataProfile 2.4 and migration
`0007_phase10m1_workspace_domain`. DS2 and Phase 11 scientific authority were
read-only dependencies.

## Workspace, Results and Viewer Delivery
- Existing persisted panels are presented as Overview, Data, Analysis
  (Plan/Execution), Results, Findings, Evidence, Report and Advanced
  (Provenance). All nine original panel kinds and exact panel URLs remain.
- Results lead with persisted result meaning, state, counts and selection
  availability before Artifact mechanics. Scientific and Developer details
  retain renderer contracts, panel IDs, compatibility and audit JSON.
- The Artifact Gallery remains metadata-first and exact. Payloads load only on
  explicit Open through scope/contract/length/checksum validation.
- Active result viewers use shared title, state, warning, focus and close
  chrome. Specialized chart/3D/trajectory/electronic controls, geometry,
  values, units, selection and series colors are unchanged.
- `UX-002` and `UX-003` are `FIXED_WITH_EVIDENCE`. UX-004 -> 12-4, UX-005 ->
  12-5, UX-006/009 -> 12-6, and UX-010 -> 12-7 remain open with their owners.

## Selection, Lifecycle and Authority
Exact compatible selection, versioned URL selection, Back/Forward/reload,
one Workspace per Job, server layout authority, cancellation, stale-response
suppression, `WorkspaceHeavyViewerLease`, inert fallback, and table/text
alternatives remain intact. No latest, fuzzy, label, filename or array-position
binding was introduced. Findings/Evidence/Inspector redesign remains Phase 12-4.

## Verification and Evidence
Local: backend `1298 passed, 50 skipped`; frontend `451 passed`; typecheck,
production build, `uv lock --check` and `git diff --check` PASS. Retained
Workspace/Artifact Gallery replay passed Chromium, Firefox, WebKit and Chromium
390x844. Deterministic evidence contains 53 hashed entries, including desktop,
mobile and partial screenshots, at
`docs/phase12/evidence/phase12_3_scientific_workspace_viewers/`.

Implementation exact-SHA CI `31370240101` passed Unit, Frontend/Typecheck/Build
and all retained browser replays, PostgreSQL/Redis/MinIO service integration,
and Linux/Windows invariant replay for
`9b38a753bda134e9c27425e1193d2980a0790731`.

`P12X3-A01` through `P12X3-A08`: `8/8`; missing/extra/duplicate/conflicting =
`0/0/0/0`. `npm audit = UNAVAILABLE` under the configured mirror policy; lock,
dependency tree and security tests pass.

## Required Markers
```text
PHASE12_3_PRODUCTION_UI_CHANGES = YES_WORKSPACE_VIEWER_PRESENTATION_ONLY
PHASE12_3_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_3_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_3_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_3_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_3_NEW_ARTIFACT_FAMILIES = 0
PHASE12_3_NEW_DATAPROFILE_VERSION = 0
PHASE12_3_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_3_NEW_DATABASE_MIGRATIONS = 0
PHASE12_3_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_3_NEW_PYTHON_DEPENDENCIES = 0
PHASE12_3_NEW_FRONTEND_DEPENDENCIES = 0
PHASE12_3_LOCKFILE_CHANGES = 0
PHASE12_3_NEW_LLM_CALL_SITES = 0
PHASE12_3_REAL_LLM_CALLS = 0
PHASE12_3_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
REGISTRY_BEFORE_12_3 = 62
REGISTRY_AFTER_12_3 = 62
DATAPROFILE_BEFORE_12_3 = 2.4
DATAPROFILE_AFTER_12_3 = 2.4
MIGRATION_AFTER_12_3 = 0007_phase10m1_workspace_domain
ONE_WORKSPACE_PER_JOB = YES
LOCAL_STORAGE_CANONICAL_AUTHORITY = NONE
SESSION_STORAGE_CANONICAL_AUTHORITY = NONE
LATEST_SCIENTIFIC_REBINDING = 0
FUZZY_SCIENTIFIC_IDENTITY = 0
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
SCIENTIFIC_COLOR_MAPPING_CHANGES = 0
INITIAL_HEAVY_PAYLOAD_REQUESTS = 0
P12X3_OWNED_PROBLEMS = UX-002, UX-003
P12X3_OWNED_PROBLEMS_CLOSED = 2
P12X3_OWNED_PROBLEMS_OPEN = 0
NEW_P0_INTRODUCED_BY_12_3 = 0
NEW_P1_INTRODUCED_BY_12_3 = 0
P12X3_ACCEPTANCE = 8/8
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI = PASS
COMPLETION_RECORDED = YES
QUEUE_ARCHIVED = PENDING_ARCHIVE_COMMIT
```

# Phase 12-5 Report / Recipe Experience Result

## Conclusion

Phase 12-5 is PASS. Exact persisted Report/Recipe 1.0 authority now has a
human-readable, result-first composition experience without new science,
execution authority, API, migration, dependency, or LLM behavior.

## Baseline And Entry

Phase 12-4 implementation `9fac62bbb2cc9069da62370ee9d02cf3150e987a`
and CI `31379672528` were verified from archive `4417e275`. Registry remained
62, DataProfile 2.4, migration `0007_phase10m1_workspace_domain`.

## Report Experience

The metadata-only source inventory explains exact eligibility, metadata-only,
unsupported, stale, and integrity states. Selection/order/captions preserve
exact source IDs and mandatory disclosures. Drafts remain session-only;
preview writes zero records; finalization requires explicit confirmation and
creates one immutable Report/Recipe pair. History and JSON/Markdown exports use
existing server authority.

## Recipe Experience

The default view explains ordered Tool steps, expected output contracts,
dependency model, execution outcome, warnings, and limitations. Exact canonical
JSON remains available as collapsed inert text. No Run or replay action exists.

## UX Problem And Acceptance

`UX-005` is `FIXED_WITH_EVIDENCE`. `UX-006` and `UX-009` remain owned by 12-6;
`UX-010` remains owned by 12-7. `P12X5-A01` through `P12X5-A08` are 8/8.

## Verification

Local: backend `1304 passed`, frontend `453 passed`, focused evidence 3 passed,
typecheck/build/lock/diff PASS. Chromium, Firefox, WebKit, and Chromium 390x844
PASS. Exact-SHA CI `31386432220` passed Unit, frontend/build/browser, Linux and
Windows invariant replay, and PostgreSQL/Redis/MinIO with zero skipped service
tests.

## Failed Candidates

`f263d704` / CI `31382890102` failed from omitted workflow working directory.
`11eb1b3b` / CI `31383949826` failed from redundant pytest in a Node-only job.
`e535ecf2` / CI `31385082975` exposed a retained M6 replay missing the new
confirmation click. All are historical-only and were fixed forward.

## Authority And Security Markers

```text
PHASE12_5_PRODUCTION_UI_CHANGES = YES_PRESENTATION_ONLY
PHASE12_5_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_5_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_5_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_5_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_5_NEW_ARTIFACT_FAMILIES = 0
PHASE12_5_NEW_DATAPROFILE_VERSION = 0
PHASE12_5_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_5_NEW_DATABASE_MIGRATIONS = 0
PHASE12_5_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_5_NEW_DEPENDENCIES = 0
PHASE12_5_NEW_LLM_CALL_SITES = 0
PHASE12_5_REAL_LLM_CALLS = 0
PHASE12_5_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
RECIPE_EXECUTION_AUTHORITY = NONE
REPORT_SCIENTIFIC_RECOMPUTATION = 0
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
REGISTRY_BEFORE_12_5 = 62
REGISTRY_AFTER_12_5 = 62
DATAPROFILE_BEFORE_12_5 = 2.4
DATAPROFILE_AFTER_12_5 = 2.4
MIGRATION_BEFORE_12_5 = 0007_phase10m1_workspace_domain
MIGRATION_AFTER_12_5 = 0007_phase10m1_workspace_domain
PHASE12_5_OWNED_PROBLEMS = UX-005
PHASE12_5_OWNED_PROBLEMS_OPEN = 0
NEW_P0_INTRODUCED_BY_12_5 = 0
P12X5_ACCEPTANCE = 8/8
IMPLEMENTATION_SHA = d20d0a1437844a9a69e71fba52cdf57dfd5144db
IMPLEMENTATION_CI = 31386432220 PASS
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI = PASS
COMPLETION_RECORDED = YES
QUEUE_ARCHIVED = PENDING_ARCHIVE_COMMIT
PHASE_12_6_EXECUTED_BY_12_5 = NO
```

## Lifecycle and Gate
Implementation commit `9b38a753bda134e9c27425e1193d2980a0790731`, CI
`31370240101` PASS. The completion record is committed directly after the one
required CI confirmation. Only the Phase 12-3 task is then removed in a direct
queue-archive commit, without waiting for another CI. Phase 12-4 remains
`REVIEWER_GATE / AWAITING REVIEWER PROMPT`; Phase 13 is approved but not queued
or executable.

# Phase 12-4 Findings / Evidence / Inspector / Provenance Experience Result

## 1. Conclusion

Phase 12-4 passes. Persisted Findings now lead through exact Evidence membership
to source Artifacts, Tool/version, Plan/Job, inputs and lineage. The Inspector is
layered as Summary, Scientific details and Provenance; developer details remain
available but subordinate.

## 2-8. Baseline, Entry And Ownership

2. Phase 12-3 baseline: implementation `9b38a753bda134e9c27425e1193d2980a0790731`, CI `31370240101` PASS.
3. Entry gate: master, clean entry worktree, HEAD/origin aligned, Phase 12-3 ancestry verified.
4. Repository state: Registry 62, DataProfile 2.4, migration `0007_phase10m1_workspace_domain`.
5. Design System authority: DS2 presentation primitives reused.
6. Phase 11 authority: read-only; no coverage or validation promotion.
7. Phase 12-4 handoff: canonical matrices and exact eight acceptance IDs resolved.
8. UX ownership: `UX-004` was the sole 12-4-owned P1 and is `FIXED_WITH_EVIDENCE`.

## 9-12. Authority Contracts

9. Production behavior changes: presentation and exact navigation only.
10. Interpretation authority: persisted `GroundedScientificInterpretation 1.0` only.
11. Claim contract: `ScientificClaim 1.0` unchanged.
12. Evidence bundle/item contracts: unchanged; exact bundle membership is validated.

## 13-23. Finding Semantics

13. Finding hierarchy: meaning, qualifier, evidence roles and exact action.
14. Claim types: Observation, Comparison, Anomaly, Warning, Scientific limitation, Recommendation and No supported conclusion remain text-qualified.
15. Qualification: DIRECT/QUALIFIED/LIMITED are labels, not fabricated probabilities.
16. Observation/comparison: rendered from persisted claim text only.
17. Warning: persistent near the affected interpretation/evidence.
18. Limitation: persistent first-class disclosure, not an ephemeral toast.
19. Recommendation: advisory and explicitly non-executable.
20. No supported conclusion: honest empty scientific outcome.
21. Partial interpretation: successful evidence scope remains visible and bounded.
22. No supported evidence: no claim is synthesized.
23. Source integrity failure: exact typed rejection; no fallback or nearest match.

## 24-36. Exact Trust Path

24. Finding to Evidence: persisted supporting/limiting/contradicting IDs only.
25. Evidence membership: bundle identity and item fields are exact-validated.
26. Supporting evidence: text role plus exact evidence selection.
27. Limiting evidence: independently visible and selectable.
28. Contradicting evidence: independently visible and selectable.
29. Evidence facts: semantic role, persisted display value and source field.
30. Numeric/unit presentation: values and units are displayed without recomputation.
31. Evidence source Artifact: exact ID/checksum/contract/version selection.
32. Source result navigation: existing Workspace panels and Selection 1.0.
33. Selection integration: `EXACT_COMPATIBLE_ONLY`.
34. Finding identity: persisted interpretation/claim IDs.
35. Evidence identity: persisted bundle/evidence item IDs.
36. Cross-panel navigation: no label, array-position, fuzzy or latest authority.

## 37-41. Inspector

37. Architecture: three progressive-disclosure layers.
38. Summary: human-readable selected-object meaning and safe actions.
39. Scientific details: exact typed facts and compatible panels.
40. Provenance: project, source scope and active panel source records.
41. Developer details: exact inert JSON remains available but collapsed by default.

## 42-55. Provenance And Compatibility

42. Provenance IA: Finding → Evidence → Artifact → Tool/version → Plan/Job → input.
43. Data source provenance: dataset/version/source scope retained.
44. Analysis context: exact Plan and Job retained.
45. Tool/version: read from persisted Evidence item.
46. Parameters: retained in existing Artifact/Inspector authority; not inferred.
47. Execution: Job/ToolCall lineage unchanged.
48. Artifact: ID, checksum and contract/version retained.
49. Evidence/claim: exact bundle, item, interpretation and claim identities retained.
50. Lineage: existing persisted references only.
51. AnalysisPlan 0.1: legacy independent/sequential semantics identified honestly.
52. AnalysisPlan 0.2: typed Artifact dependency semantics identified honestly.
53. Historical compatibility: retained tests pass.
54. Stale/missing source: explicit unavailable/error state.
55. Cross-scope rejection: project/job/bundle/item mismatch is rejected.

## 56-63. Boundaries And States

56. Wording audit: no unqualified scientific certainty or fabricated confidence.
57. Phase 11 presentation: support, validation, reproducibility and presentation remain separate.
58. Report boundary: authority/workflow unchanged; owned by 12-5.
59. Recipe boundary: non-executable authority unchanged.
60. Workspace boundary: one Workspace per Job and server/URL/memory authority unchanged.
61. Viewer boundary: no scientific viewer computation or series mapping change.
62. Loading UX: persisted reference loading has bounded status.
63. Error/recovery: failed exact source validation preserves context and does not substitute.

## 64-73. Responsive And Browser Evidence

64. Desktop 1440x900: PASS.
65. Desktop 1280x720: PASS.
66. Mobile 390x844: PASS with Context drawer and one active panel authority.
67. 200% zoom: shared trust-path matrix PASS.
68. Keyboard/focus: Finding, Evidence and Inspector paths PASS; focus restore PASS.
69. Reduced motion: PASS.
70. Accessibility foundation: non-color roles/status and 44px mobile actions PASS.
71. Browser matrix: Chromium, Firefox and WebKit PASS; console/page/external request errors 0.
72. Trust-path replay: Findings, Evidence, Inspector and Provenance screenshots retained.
73. Interaction comparison: no new execution action or route/API family.

## 74-84. Non-Change, Security And Handoff

74. Scientific payload semantic diff: 0.
75. Interpretation contract semantic diff: 0.
76. Reinterpretation: 0; production consumes persisted claims/evidence.
77. Execution growth: 0; no plan/job/queue action added.
78. Security: inert text, no Artifact HTML/JS/iframe/external URL execution; secret scan PASS.
79. LLM/DeepSeek: new call sites 0, real calls 0, provider policy unchanged.
80. Database/API/dependencies: no schema, migration, public API, dependency or lock change.
81. Registry/DataProfile: 62 and 2.4 before/after.
82. Problem closure: `UX-004` 1/1 closed; new P0/P1 0.
83. Deferred: `UX-005`→12-5, `UX-006`/`UX-009`→12-6, `UX-010`→12-7 remain typed/open.
84. Phase 12-5 handoff: exact Report/Recipe source and warning-preservation constraints recorded; task not created by 12-4.

## 85-93. Verification And Evidence

85. Backend: `1301 passed` locally; exact-SHA CI PASS.
86. Frontend: `453 passed`.
87. Typecheck: PASS.
88. Production build: PASS.
89. Service-backed: `48 passed`, `0 skipped`, `0 failed`, `0 errors`.
90. Linux/Windows sealed invariant replay: PASS.
91. npm audit: `UNAVAILABLE` under configured mirror policy; lock/dependency/security checks PASS.
92. Evidence inventory: 74 normalized files including desktop/mobile browser captures.
93. Manifest: missing 0, extra 0, hash mismatch 0, secret-bearing evidence 0.

## 94-103. Lifecycle And Final State

94. Files changed: Workspace presentation/selection, focused tests, browser harness, Phase 12 docs/evidence, persistent state and queue validators.
95. Acceptance registry: `P12X4-A01` through `P12X4-A08`, 8/8.
96. Implementation commit: `9fac62bbb2cc9069da62370ee9d02cf3150e987a`.
97. Implementation CI: `31379672528` PASS.
98. Failed implementation candidates: none.
99. Completion record: committed directly after the single required CI confirmation.
100. Queue archive: follows as a direct commit without a second CI wait.
101. Queue state at completion record: 12-4 retained as complete pending archive; 12-5/12-6 remain pending.
102. Phase 12-5 gate: reviewer prompt exists as a pending task; 12-4 does not execute it.
103. Final repository state is recorded after queue archive.

## Mandatory Markers

```text
PHASE12_4_PRODUCTION_UI_CHANGES = YES_FINDINGS_EVIDENCE_INSPECTOR_PROVENANCE_PRESENTATION
PHASE12_4_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_4_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_4_INTERPRETATION_SEMANTIC_CHANGES = 0
PHASE12_4_SCIENTIFIC_CLAIM_CONTRACT_CHANGES = 0
PHASE12_4_EVIDENCE_CONTRACT_CHANGES = 0
PHASE12_4_GROUNDING_VALIDATOR_CHANGES = 0
PHASE12_4_ARTIFACT_CONTRACT_CHANGES = 0
PHASE12_4_WORKSPACE_AUTHORITY_CHANGES = 0
PHASE12_4_SELECTION_CONTRACT_CHANGES = 0
PHASE12_4_REPORT_AUTHORITY_CHANGES = 0
PHASE12_4_RECIPE_AUTHORITY_CHANGES = 0
PHASE12_4_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_4_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_4_NEW_ARTIFACT_FAMILIES = 0
PHASE12_4_NEW_DATAPROFILE_VERSION = 0
PHASE12_4_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_4_NEW_DATABASE_MIGRATIONS = 0
PHASE12_4_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_4_NEW_DEPENDENCIES = 0
PHASE12_4_LOCKFILE_CHANGES = 0
PHASE12_4_NEW_LLM_CALL_SITES = 0
PHASE12_4_REAL_LLM_CALLS = 0
PHASE12_4_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
FINDING_TO_EVIDENCE_EXACT_LINKING = PASS
EVIDENCE_TO_ARTIFACT_EXACT_LINKING = PASS
ARTIFACT_TO_TOOL_VERSION_TRACEABILITY = PASS
INPUT_IDENTITY_TRACEABILITY = PASS
PROVENANCE_TRACEABILITY = PASS
FUZZY_FINDING_EVIDENCE_LINKING = 0
DISPLAY_LABEL_PROVENANCE_AUTHORITY = 0
ARRAY_POSITION_PROVENANCE_AUTHORITY = 0
INSPECTOR_SUMMARY_LAYER = PASS
INSPECTOR_SCIENTIFIC_DETAILS_LAYER = PASS
INSPECTOR_PROVENANCE_LAYER = PASS
DEVELOPER_DETAILS_AVAILABLE = YES
RAW_JSON_DEFAULT_PRIMARY_LAYER = NO
INSPECTOR_SCIENTIFIC_RECOMPUTATION = 0
SUPPORTED_EQUALS_VALIDATED = NO
MAPPING_ONLY_VISUAL_UPGRADE = 0
NOT_APPLICABLE_VISUAL_UPGRADE = 0
V4_VISUAL_FABRICATION = 0
BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO
SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
RECOMMENDATION_EXECUTION_AUTHORITY = NONE
RECOMMENDATION_AUTO_PLAN = 0
RECOMMENDATION_AUTO_JOB = 0
RECOMMENDATION_AUTO_QUEUE = 0
REGISTRY_BEFORE_12_4 = 62
REGISTRY_AFTER_12_4 = 62
DATAPROFILE_BEFORE_12_4 = 2.4
DATAPROFILE_AFTER_12_4 = 2.4
MIGRATION_BEFORE_12_4 = 0007_phase10m1_workspace_domain
MIGRATION_AFTER_12_4 = 0007_phase10m1_workspace_domain
PHASE12_4_OWNED_PROBLEMS = UX-004
PHASE12_4_OWNED_PROBLEM_COUNT = 1
PHASE12_4_OWNED_PROBLEMS_CLOSED = 1
PHASE12_4_OWNED_PROBLEMS_OPEN = 0
NEW_P0_INTRODUCED_BY_12_4 = 0
NEW_P1_INTRODUCED_BY_12_4 = 0
P12X4_ACCEPTANCE = 8/8
FINDINGS_KEYBOARD = PASS
EVIDENCE_KEYBOARD = PASS
INSPECTOR_KEYBOARD = PASS
INSPECTOR_FOCUS_RESTORE = PASS
FINDING_STATUS_NON_COLOR = PASS
EVIDENCE_ROLE_NON_COLOR = PASS
MOBILE_TOUCH_TARGETS = PASS
REDUCED_MOTION = PASS
FULL_PRODUCT_ACCESSIBILITY_COMPLETE = NO
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI = PASS
COMPLETION_RECORDED = YES
QUEUE_ARCHIVED = PENDING_ARCHIVE_COMMIT
```
# Phase 12-6 Responsive / Mobile / Accessibility Closure Result

## 1-9. Conclusion, Baseline, Entry, Authority, and Ownership

Phase 12-6 is `PASS / RESPONSIVE_MOBILE_ACCESSIBILITY_CLOSED /
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI / COMPLETION_RECORDED`. Phase 12-5
implementation `d20d0a1437844a9a69e71fba52cdf57dfd5144db` / CI `31386432220`
is the entry baseline. DS2 and Phase 11 remain read-only authorities. The sole
owned problems `UX-006` (P1) and `UX-009` (P2) are closed; `UX-010` remains
open with 12-7. Production changes are responsive/accessibility presentation
only.

## 10-26. Responsive and Mobile Surfaces

All inventoried responsive surfaces are classified. Global shell, Data,
Planner, clarification, Plan, execution, Workspace, Results, scientific
viewers, Findings, Evidence, Inspector, Provenance, Report and Recipe retain
their existing routes and authority. At `390x844`, the product uses one active
Workspace panel, context drawer, panel switcher and Inspector bottom sheet.
Touch controls are at least 44 CSS px; long labels and scientific identities
wrap; dense tables use bounded horizontal scroll. Mobile journeys M1-M14 are
audited with no unclassified or unaudited case.

## 27-48. Keyboard, Semantics, Zoom, Contrast, and Motion

Keyboard journeys K1-K10 pass. Skip navigation reaches the primary Planner or
active Workspace result. The data-context separator supports Arrow Left/Right
and Home/End. Dialogs, drawers and sheets trap focus, close with Escape and
restore trigger focus. Landmarks, headings, accessible names, form labels and
async live regions are present. State is not color-only. Required touch,
contrast, 200% zoom, reflow and overflow failures are zero. Forced-colors and
`prefers-reduced-motion` smoke tests pass. Screen-reader status is honestly
`PASS_BY_DOM_ARIA_AND_BROWSER_EVIDENCE`; formal certification is not claimed.

## 49-61. Scientific Visualization and State Accessibility

Tables and charts retain numeric/text alternatives. Three-dimensional surfaces
retain structured metadata, warnings, limitations and Inspector access.
Tooltips have focus/persistent equivalents; required drag behavior has keyboard
equivalence. Error, empty, loading, unsupported, stale and partial states retain
typed text. Scientific warnings and support/validation qualifiers remain
accessible. Security-tree evidence contains no secret or executable Artifact
content.

## 62-71. Non-Change, Closure, Limits, and Handoff

Scientific payload, contract, Global IA, Workspace IA, Inspector architecture,
Report and Recipe authority diffs are zero. Accepted limitations: no formal
WCAG certification and no claim that every spatial 3D interaction has an
identical screen-reader interaction. Phase 12-7 is `REVIEWER_GATE /
AWAITING REVIEWER PROMPT`, owns `UX-010`, and has no executable task.

## 72-87. Verification and Evidence

- Browser matrix: Chromium PASS, Firefox PASS, WebKit PASS, Chromium 390x844 PASS.
- Accessibility focused tests: 5 passed; component-focused suite: 60 passed.
- Backend regression: 1309 passed, 50 skipped locally; CI service-backed tests passed with zero skips.
- Frontend regression: 455 passed.
- Typecheck, production build, `uv lock --check`, `git diff --check`: PASS.
- PostgreSQL/Redis/MinIO: PASS in CI.
- Linux/Windows invariant replay: PASS.
- npm audit: UNAVAILABLE under configured mirror policy; lock and security tests PASS.
- Evidence: 54 manifest entries, missing/extra/hash mismatch = 0.
- Acceptance: `P12X6-A01` through `P12X6-A08`, 8/8.

## 88-95. Lifecycle and Final State

Failed implementation candidate `17450c3f3704a55e4302eab9f72e66821076fa1b`
/ CI `31391903172` is historical only. All non-new gates passed; the new browser
server timed out after prior dev replays replaced production `.next` output.
Corrected implementation `e2beacb0d1e60e5bfccbcd07271f47f5736a221d`
/ exact-SHA CI `31393608850` passed. This result is the direct completion record;
the next direct commit removes only the completed 12-6 queue block. No separate
completion/archive CI is awaited. Phase 12-7 and Phase 13 executable tasks are absent.

Mandatory markers:

```text
PHASE12_6_PRODUCTION_UI_CHANGES = YES_RESPONSIVE_MOBILE_ACCESSIBILITY
PHASE12_6_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_6_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_6_GLOBAL_IA_CHANGES = 0
PHASE12_6_PLANNER_SEMANTIC_CHANGES = 0
PHASE12_6_WORKSPACE_AUTHORITY_CHANGES = 0
PHASE12_6_SELECTION_SEMANTIC_CHANGES = 0
PHASE12_6_ARTIFACT_CONTRACT_CHANGES = 0
PHASE12_6_INTERPRETATION_CONTRACT_CHANGES = 0
PHASE12_6_REPORT_CONTRACT_CHANGES = 0
PHASE12_6_RECIPE_CONTRACT_CHANGES = 0
PHASE12_6_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_6_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_6_NEW_ARTIFACT_FAMILIES = 0
PHASE12_6_NEW_DATAPROFILE_VERSION = 0
PHASE12_6_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_6_NEW_DATABASE_MIGRATIONS = 0
PHASE12_6_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_6_NEW_DEPENDENCIES = 0
PHASE12_6_LOCKFILE_CHANGES = 0
PHASE12_6_NEW_LLM_CALL_SITES = 0
PHASE12_6_REAL_LLM_CALLS = 0
PHASE12_6_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
RESPONSIVE_SURFACE_UNCLASSIFIED = 0
MOBILE_CORE_WORKFLOWS_COMPLETE = YES
UNEXPECTED_PAGE_HORIZONTAL_OVERFLOW = 0
MOBILE_GLOBAL_NAVIGATION = PASS
MOBILE_PLANNER = PASS
MOBILE_WORKSPACE = PASS
MOBILE_SCIENTIFIC_VIEWERS = PASS
MOBILE_FINDINGS_EVIDENCE = PASS
MOBILE_INSPECTOR = PASS
MOBILE_REPORT_RECIPE = PASS
CORE_KEYBOARD_WORKFLOWS = PASS
VISIBLE_FOCUS_REQUIRED_CASES = PASS
FOCUS_RESTORATION_REQUIRED_CASES = PASS
ACCESSIBLE_NAME_REQUIRED_CASES = PASS
FORM_LABEL_REQUIRED_CASES = PASS
HEADING_LANDMARK_REQUIRED_CASES = PASS
ASYNC_STATUS_ANNOUNCEMENTS = PASS
STATUS_COLOR_ONLY_MEANING = 0
REQUIRED_TOUCH_TARGET_FAILURES = 0
CONTRAST_REQUIRED_FAILURES = 0
ZOOM_200_REQUIRED_FAILURES = 0
REFLOW_REQUIRED_FAILURES = 0
REDUCED_MOTION_REQUIRED_CASES = PASS
FULL_PRODUCT_ACCESSIBILITY_ENGINEERING_CLOSURE = YES
FORMAL_ACCESSIBILITY_CERTIFICATION = NO
CHART_ACCESSIBLE_DATA_ALTERNATIVE_REQUIRED_CASES = PASS
THREE_D_STRUCTURED_ALTERNATIVE_REQUIRED_CASES = PASS
PLOTLY_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
WEBGL_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
ACCESSIBLE_ALTERNATIVE_SCIENTIFIC_RECOMPUTATION = 0
SCIENTIFIC_SERIES_COLOR_SEMANTIC_CHANGES = 0
SUPPORTED_EQUALS_VALIDATED = NO
MAPPING_ONLY_VISUAL_UPGRADE = 0
NOT_APPLICABLE_VISUAL_UPGRADE = 0
V4_VISUAL_FABRICATION = 0
BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO
SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO
ACCESSIBILITY_PASS_EQUALS_SCIENTIFIC_PASS = NO
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
REGISTRY_BEFORE_12_6 = 62
REGISTRY_AFTER_12_6 = 62
DATAPROFILE_BEFORE_12_6 = 2.4
DATAPROFILE_AFTER_12_6 = 2.4
MIGRATION_BEFORE_12_6 = 0007_phase10m1_workspace_domain
MIGRATION_AFTER_12_6 = 0007_phase10m1_workspace_domain
PHASE12_6_OWNED_PROBLEMS = UX-006, UX-009
PHASE12_6_OWNED_PROBLEM_COUNT = 2
PHASE12_6_OWNED_PROBLEMS_CLOSED = 2
PHASE12_6_OWNED_PROBLEMS_OPEN = 0
NEW_P0_INTRODUCED_BY_12_6 = 0
NEW_P1_INTRODUCED_BY_12_6 = 0
P12X6_ACCEPTANCE = 8/8
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
COMPLETION_RECORDED
PHASE_12_7_EXECUTABLE_TASK_CREATED = NO
PHASE_13_EXECUTABLE_TASK_CREATED = NO
```

# Phase 12-7 Cross-Product UX Validation + Design Evidence Closure Result

## 1. Conclusion
Phase 12-7 is `PASS / CROSS_PRODUCT_UX_VALIDATED / DESIGN_EVIDENCE_SEALED / IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI / COMPLETION_RECORDED`. Phase 12 is `COMPLETE / PRODUCT_EXPERIENCE_REDESIGN_VALIDATED_AND_SEALED` within explicit limits.

## 2. Phase 12-6 Baseline
Implementation `e2beacb0d1e60e5bfccbcd07271f47f5736a221d`, CI `31393608850`, completion `c861bd7`, and archive `7f47bbbcf494a4592f5c73f5471030cdae91c635` are verified.

## 3. Entry Gate
`PHASE_12_7_ENTRY_GATE = PASS`; the sole user-added queue block was admitted after the clean `7f47bbb` baseline.

## 4. Repository State
Entry branch was `master`, `HEAD == origin/master`, with only the authorized queue admission delta after task creation.

## 5. Phase 12 Authority Chain
Phase 12-0 decisions resolve through the retained 12-1 through 12-6 implementations and this final validation.

## 6. Phase 11 Scientific Authority
Registry 62, DataProfile 2.4, AnalysisPlan 0.1/0.2 and migration `0007_phase10m1_workspace_domain` remain read-only.

## 7. Design System Authority
DS2 version 2.0 remains presentation-only; no scientific identity binds to its semantic hash.

## 8. Phase 12 Decision Registry
`P12-D001` through `P12-D020`: 20 expected, 20 resolved, 0 violated.

## 9. UX Problem Final Ownership
All original owners and severities for `UX-001` through `UX-010` are retained.

## 10. UX-010 / Final Problem Closure
`UX-010` is `FIXED_WITH_EVIDENCE` through cross-product DS2 density, toolbar, status, terminology and viewport consistency validation.

## 11. Full Phase 12 Problem Reconciliation
Ten problems are closed; P0/P1/P2/P3 open counts are all zero and unassigned count is zero.

## 12. Phase 12 Acceptance Reconciliation
68 canonical IDs pass: 12 for 12-0 and 8 each for 12-1 through 12-7; missing/duplicate/conflicting counts are zero.

## 13. P12X7 Acceptance
`P12X7-A01` through `P12X7-A08` pass exactly: `P12X7_ACCEPTANCE = 8/8`.

## 14. Canonical Journey Registry
The eleven Phase 12-0 journeys A-K remain unchanged and authoritative.

## 15. Journey 1 - New Data
Data selection, Profile/readiness and eligible analysis discovery pass without inferred semantics.

## 16. Journey 2 - Natural-Language Analysis
Prompt, clarification, eligibility, human plan, execution and Workspace transition preserve context and non-ready blocking.

## 17. Journey 3 - Professional Analysis
Professional results retain dense presentation, limitations, diagnostics and exact provenance.

## 18. Journey 4 - Result Understanding
Result to Viewer to Finding/Evidence/Inspector/Provenance is meaning-first and exactly traceable.

## 19. Journey 5 - Report / Recipe
Source discovery, disclosures, preview/finalization and inert Recipe presentation pass with no generated science.

## 20. Journey 6 - Historical Recovery
Historical Workspace and records open by exact identity with no latest rebind.

## 21. Journey 7 - Unsupported Input
Typed unsupported status, explanation and supported recovery remain visible; readiness is not fabricated.

## 22. Journey 8 - Partial Execution
Successful, failed and blocked branches remain distinguishable and trustworthy disclosures persist.

## 23. Journey 9 - Provider Setup
Server-owned DeepSeek state is understandable; browser secret input and direct provider calls remain absent.

## 24. Journey 10 - Mobile Inspection
390x844 retains one active Workspace panel, context drawer, panel switcher and Inspector sheet authority.

## 25. Journey 11 - Developer Provenance
Exact identifiers and raw developer detail remain available but subordinate and inert.

## 26. Journey Aggregate
11 expected/replayed/passed; 0 failed, blocked or unaudited.

## 27. Interaction Baseline Comparison
Automation measurements remain interaction proxies; no human time-on-task or usability-study claim is made.

## 28. Product Experience Principles
All twelve sealed principles pass, including meaning before mechanism, result before Artifact and no UX-created science.

## 29. Global IA Validation
Home, Data, Analyses, Workspaces, Reports and Settings remain unchanged.

## 30. Workspace IA Validation
Overview, Data, Analysis, Results, Findings, Evidence, Report and Advanced remain unchanged with one active panel.

## 31. Planner Consistency
Human-readable stages, one primary action and context-preserving typed recovery pass.

## 32. Workspace Consistency
Server Workspace identity, URL panel/selection authority and transient memory boundaries remain exact.

## 33. Viewer Consistency
Shared title, toolbar, status, warning, loading and alternatives pass while specialized controls retain scientific semantics.

## 34. Findings / Evidence Consistency
Persisted claims and supporting/limiting/contradicting evidence retain exact membership.

## 35. Inspector Consistency
Summary, Scientific Details and Provenance remain the three layers.

## 36. Provenance Consistency
Artifact, Tool/version, input identity, lineage and hashes remain exact and subordinate.

## 37. Report / Recipe Consistency
Meaning-first report/recipe presentation retains mandatory disclosures and zero execution authority.

## 38. Terminology Consistency
18 canonical terms resolve in en-US and zh-CN with zero required inconsistency.

## 39. Status Consistency
Ten DS2 status families map with text; no color-only meaning or invented backend status exists.

## 40. Warning / Limitation Consistency
Scientific limitations remain persistent and are never reduced to dismissible toast feedback.

## 41. Design System Consistency
DS2 token, component migration and visual vocabulary audits remain complete with zero uncontrolled authority.

## 42. UI Surface Final Coverage
All Phase 12-0 surfaces retain a final disposition; `UI_SURFACE_UNCLASSIFIED = 0`.

## 43. Component Final Coverage
All components retain migration dispositions; `UI_COMPONENT_UNCLASSIFIED = 0`.

## 44. Desktop 1440x900
Chromium, Firefox and WebKit pass hierarchy, focus, wrapping, overflow and request checks.

## 45. Desktop 1280x720
Chromium passes with zero unexpected horizontal overflow.

## 46. Mobile 390x844
Chromium passes with zero required touch or overflow failures.

## 47. Keyboard
Core keyboard workflows and Planner resize Arrow/Home/End behavior pass.

## 48. Focus / Restoration
Visible focus and required restoration cases pass.

## 49. Screen Reader Semantics
Landmarks, headings, names and status semantics pass engineering checks; no formal certification is claimed.

## 50. Touch Targets
Required mobile controls meet 44x44 CSS px; failures = 0.

## 51. Contrast
Required WCAG-like AA engineering checks have zero failures; formal certification = no.

## 52. Non-Color State
`STATUS_COLOR_ONLY_MEANING = 0`.

## 53. 200% Zoom
Required action clipping and unrecoverable overflow failures = 0.

## 54. Reflow
Planner, Workspace and Report reflow; scientific tables use bounded scrolling.

## 55. Reduced Motion
All required cases pass and continuous decorative motion count is zero.

## 56. Chart Accessibility
Required chart data alternatives pass; Plotly numeric authority is none.

## 57. 3D Accessibility
Required structured alternatives pass; WebGL numeric authority is none.

## 58. Heavy Viewer Lifecycle
One active heavy viewer maximum, zero inactive requests and zero duplicate canvas/listener growth are retained.

## 59. Loading / Empty / Error States
Shared shells and context-preserving recovery remain consistent.

## 60. Unsupported / Stale / Partial States
All remain typed, text-bearing and distinct from disabled/loading states.

## 61. Before / After Evidence
Phase 12-0 is the before authority; 12-1 through 12-7 are indexed after evidence. Screenshots carry no numeric authority.

## 62. Scientific Payload Non-Change
Value, unit, claim and identity semantic differences are zero.

## 63. Frontend No-Recomputation
`PHASE12_7_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0`.

## 64. Workspace Authority Non-Change
One Workspace per Job, persistence, revision, URL and local/session storage authority remain unchanged.

## 65. Selection Authority Non-Change
Exact selection identity is retained; latest, fuzzy, filename, label and array-position authority remain absent.

## 66. Claim/Evidence Contract Non-Change
Interpretation and claim/evidence contracts changed = 0.

## 67. Report/Recipe Contract Non-Change
Report and Recipe contracts changed = 0; Recipe execution authority = none.

## 68. Phase 11 Authority Non-Change
Tool/input coverage, validation levels, public claims and scientific limitations are unchanged.

## 69. Accepted UX Limitations
No formal accessibility certification, assistive-technology study, human study or browser pixel equality is claimed.

## 70. Final Design Evidence Manifest
63 deterministic members pass with missing/extra/hash-mismatch counts zero and implementation CI `31397995499`.

## 71. Phase 12 Product Experience Baseline
`PHASE12_PRODUCT_EXPERIENCE_BASELINE = SEALED`.

## 72. Baseline Determinism
`PHASE12_PRODUCT_EXPERIENCE_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4`; regeneration is stable.

## 73. Phase 13 Handoff
Seven roadmap demo families and the complete resource-to-Report/Recipe path are handed off without execution authority.

## 74. Backend Regression
Local backend: `1314 passed, 50 skipped`; the skipped service cases run separately in CI.

## 75. Frontend Regression
71 files and `455 passed`.

## 76. Typecheck
PASS.

## 77. Build
PASS; existing Plotly/glslify dynamic dependency warnings remain non-blocking.

## 78. Lock
`uv lock --check` PASS; lockfile changes = 0.

## 79. Service Regression
PostgreSQL, Redis and MinIO required integration passed with zero skipped in CI.

## 80. Linux/Windows Replay
Both sealed invariant replays pass; numeric cross-platform validation remains governed by Phase 11.

## 81. Browser Matrix
Chromium, Firefox, WebKit, Chromium 1280x720 and Chromium 390x844 pass with zero console/page/external-request errors.

## 82. Security
Arbitrary execution, active Artifact content, Recipe/recommendation execution, cross-scope leakage and secret disclosure gates pass.

## 83. Secret Scan
Secret-bearing evidence, credentials, private paths and real LLM calls = 0.

## 84. Evidence Inventory
Journey, consistency, accessibility, authority, baseline, handoff, browser and screenshot evidence is retained under the X7 evidence root.

## 85. Files Changed
Audit/evidence tooling, test-only browser replay, docs, evidence, persistent state and queue records only; production source changes = 0.

## 86. Implementation Commit
`8fb5dcbe54fbbcd32677107abb5f4117bd04948d`.

## 87. Implementation Exact-SHA CI
CI `31397995499` PASS across all required jobs.

## 88. Failed Candidates
Phase 12-7 failed candidates = none. The 12-6 historical failed candidate remains retained and non-authoritative.

## 89. Completion Record
This direct completion record follows successful implementation CI; no separate completion CI is awaited.

## 90. Queue Archive
The next direct commit removes only the completed Phase 12-7 task; no archive CI is awaited or claimed verified.

## 91. Queue State
Completion-record state retains one completed block pending immediate archive; final `TASK_BLOCK_COUNT = 0` after that direct commit.

## 92. Phase 12 Final Status
`COMPLETE / PRODUCT_EXPERIENCE_REDESIGN_VALIDATED_AND_SEALED`.

## 93. Phase 13 Reviewer Gate
`REVIEWER_GATE / AWAITING REVIEWER PROMPT`; executable task created = no.

## 94. Final Repository State
After the next direct archive push: `master`, `HEAD == origin/master`, clean worktree, Registry 62, DataProfile 2.4, migration 0007, empty queue.

```text
PHASE12_7_PRODUCTION_UI_CHANGES = NO
PHASE12_7_BACKEND_BEHAVIOR_CHANGES = 0
PHASE12_7_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE12_7_GLOBAL_IA_CHANGES = 0
PHASE12_7_WORKSPACE_IA_CHANGES = 0
PHASE12_7_PLANNER_SEMANTIC_CHANGES = 0
PHASE12_7_ARTIFACT_CONTRACT_CHANGES = 0
PHASE12_7_SELECTION_SEMANTIC_CHANGES = 0
PHASE12_7_INTERPRETATION_CONTRACT_CHANGES = 0
PHASE12_7_REPORT_CONTRACT_CHANGES = 0
PHASE12_7_RECIPE_CONTRACT_CHANGES = 0
PHASE12_7_NEW_SCIENTIFIC_TOOLS = 0
PHASE12_7_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE12_7_NEW_ARTIFACT_FAMILIES = 0
PHASE12_7_NEW_DATAPROFILE_VERSION = 0
PHASE12_7_NEW_ANALYSISPLAN_VERSION = 0
PHASE12_7_NEW_DATABASE_MIGRATIONS = 0
PHASE12_7_NEW_PUBLIC_API_FAMILIES = 0
PHASE12_7_NEW_DEPENDENCIES = 0
PHASE12_7_LOCKFILE_CHANGES = 0
PHASE12_7_NEW_LLM_CALL_SITES = 0
PHASE12_7_REAL_LLM_CALLS = 0
PHASE12_7_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
UI_SURFACE_UNCLASSIFIED = 0
UI_COMPONENT_UNCLASSIFIED = 0
UX_PROBLEM_UNASSIGNED = 0
PHASE12_ALL_OWNED_PROBLEMS_OPEN = 0
CANONICAL_JOURNEYS_UNAUDITED = 0
PHASE12_IMPLEMENTATION_CRITICAL_TBD = 0
UNMAPPED_USER_VISIBLE_STATUS_FAMILIES = 0
NEW_P0_INTRODUCED_BY_12_7 = 0
NEW_P1_INTRODUCED_BY_12_7 = 0
PHASE12_DESIGN_SYSTEM_VERSION = 2.0
DESIGN_SYSTEM_TOKEN_REGISTRY_COMPLETE = YES
UNCLASSIFIED_LEGACY_TOKENS = 0
UNCONTROLLED_HARDCODED_DESIGN_VALUES = 0
UI_COMPONENT_MIGRATION_UNCLASSIFIED = 0
CANONICAL_JOURNEYS_EXPECTED = 11
CANONICAL_JOURNEYS_PASS = 11
CANONICAL_JOURNEYS_FAIL = 0
CANONICAL_JOURNEYS_BLOCKED = 0
MOBILE_CORE_WORKFLOWS_COMPLETE = YES
CORE_KEYBOARD_WORKFLOWS = PASS
VISIBLE_FOCUS_REQUIRED_CASES = PASS
FOCUS_RESTORATION_REQUIRED_CASES = PASS
ACCESSIBLE_NAME_REQUIRED_CASES = PASS
STATUS_COLOR_ONLY_MEANING = 0
REQUIRED_TOUCH_TARGET_FAILURES = 0
CONTRAST_REQUIRED_FAILURES = 0
ZOOM_200_REQUIRED_FAILURES = 0
REFLOW_REQUIRED_FAILURES = 0
UNEXPECTED_PAGE_HORIZONTAL_OVERFLOW = 0
REDUCED_MOTION_REQUIRED_CASES = PASS
ACCESSIBILITY_ENGINEERING_TARGET_MET = YES
FORMAL_ACCESSIBILITY_CERTIFICATION = NO
CHART_ACCESSIBLE_DATA_ALTERNATIVE_REQUIRED_CASES = PASS
THREE_D_STRUCTURED_ALTERNATIVE_REQUIRED_CASES = PASS
PLOTLY_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
WEBGL_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
SUPPORTED_EQUALS_VALIDATED = NO
REPORT_INCLUDED_EQUALS_VALIDATED = NO
RECIPE_EXISTS_EQUALS_REPRODUCIBILITY_VALIDATED = NO
ACCESSIBILITY_PASS_EQUALS_SCIENTIFIC_PASS = NO
BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO
SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO
MAPPING_ONLY_VISUAL_UPGRADE = 0
NOT_APPLICABLE_VISUAL_UPGRADE = 0
V4_VISUAL_FABRICATION = 0
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
REGISTRY_BEFORE_12_7 = 62
REGISTRY_AFTER_12_7 = 62
DATAPROFILE_BEFORE_12_7 = 2.4
DATAPROFILE_AFTER_12_7 = 2.4
MIGRATION_BEFORE_12_7 = 0007_phase10m1_workspace_domain
MIGRATION_AFTER_12_7 = 0007_phase10m1_workspace_domain
PHASE12_7_OWNED_PROBLEMS = UX-010
PHASE12_7_OWNED_PROBLEM_COUNT = 1
PHASE12_7_OWNED_PROBLEMS_CLOSED = 1
PHASE12_7_OWNED_PROBLEMS_OPEN = 0
P12X7_ACCEPTANCE = 8/8
PHASE12_ALL_ACCEPTANCE = 68/68
PHASE12_PRODUCT_EXPERIENCE_BASELINE = SEALED
PHASE12_PRODUCT_EXPERIENCE_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
PHASE12_BASELINE_DETERMINISM = PASS
PHASE12_FINAL_DESIGN_EVIDENCE_MANIFEST = PASS
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
COMPLETION_RECORDED
PHASE13_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
```

# Phase 13-0 Final Fact Alignment + Release Scope Seal Result

## 1. Conclusion
`PASS / FINAL_FACTS_ALIGNED / INITIAL_RELEASE_SCOPE_SEALED / COMPLETION_RECORDED`. Phase 13-0 changes no production or scientific behavior. The seven final demonstrations are precisely contracted but not executed.

## 2. Phase 12 Baseline
Phase 12 is `COMPLETE / PRODUCT_EXPERIENCE_REDESIGN_VALIDATED_AND_SEALED`; baseline `29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4` regenerated deterministically.

## 3. Entry Gate
Entry baseline `69d53376b188a20db2c3cc2c28824afb5971621d`, master, clean worktree, empty queue, and absent Phase 13-1/13-2/14 tasks were verified before admission.

## 4. Repository State
Phase 12-7 implementation `8fb5dcbe54fbbcd32677107abb5f4117bd04948d`, CI `31397995499`, completion `a369bf26aca1b11522aed97e5baa1fa9017d673e`, archive `69d53376b188a20db2c3cc2c28824afb5971621d` resolve and are ancestors.

## 5. Phase 13 Handoff Integrity
The unique Phase 13 final-product-closure handoff resolves to the Phase 11 and Phase 12 sealed authorities and exactly seven demo families.

## 6. Phase 11 Scientific Authority
`COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS`; baseline `5273b5e866e950c592fe757c2e7bde2d4ede9551f7eb406d0744bb6dcf7d93cb` remains read-only.

## 7. Phase 12 Product Experience Authority
Acceptance `68/68`, journeys `11/11`, UX problems `10/10 closed`; no Phase 12 baseline mutation occurred.

## 8. Registry Reconciliation
Live Registry, documented inventory and release matrix each contain 62 unique versioned Tools, assigned exactly once.

## 9. DataProfile / Analysis Contract Baseline
DataProfile `2.4`, AnalysisIntent `1.0`, EligibilityResolution `1.0`, AnalysisPlan `0.1/0.2`, migration `0007_phase10m1_workspace_domain`.

## 10. Input Support Matrix
The sealed 14-row Phase 11 matrix is retained with zero support promotions: 10 direct-supported rows, one mapping-only row and three unsupported rows.

## 11. Tool / Capability Matrix
Twenty-six release-relevant capability families reconcile all 62 Tools plus product-composition authorities.

## 12. Product Support
Product support remains independent from scientific validation, reproducibility and presentation evidence.

## 13. Scientific Validation
Golden records `12`: `8 PASS_INVARIANT`, `4 NOT_APPLICABLE`, `0 failures`; V4 promotions remain `0`.

## 14. Cross-Platform Reproducibility
Locked Linux and Windows invariant replay PASS; numeric cross-platform reference validation remains `NOT_APPLICABLE`; macOS is not a current scientific release target.

## 15. Presentation Validation
Chromium, Firefox, WebKit and Chromium `390x844` PASS as presentation authority only.

## 16. Initial Release Product Positioning
`Material Data Intelligence and Scientific Visualization Platform`, not a generic AI wrapper.

## 17. Initial Release Capability Claims
Claims cover bounded natural-language planning, deterministic registered execution, persisted Artifacts, Workspace, Evidence, Report and non-executable Recipe.

## 18. Forbidden Claims
Forbidden wording includes all-tools independent validation, all-numeric cross-platform validation, formal WCAG certification, autonomous research, arbitrary workflows, DFT/GW execution, Rietveld refinement and executable Recipes.

## 19. Known Limitations
Six explicit limitations retain V4=0, cross-platform numeric N/A, macOS scope, accessibility certification boundary, bounded 3D alternatives, and mapping-only input/example coverage.

## 20. Future Scope
Advanced diffraction, electronic, topology, defect, trajectory and transport families remain documented and unqueued.

## 21. Not Planned Scope
Arbitrary DAG/code/notebook execution, runtime replanning, RAG, marketplace, SaaS/billing/enterprise infrastructure and unrestricted providers remain Not Planned.

## 22. Provider Policy
Real provider is DeepSeek only at `https://api.deepseek.com`, models `deepseek-v4-flash` and `deepseek-v4-pro`, key source `DEEPSEEK_KEY`; Phase 13-0 made zero real calls.

## 23. Security Boundary
Artifacts and Recipes remain inert; no arbitrary Python, shell, notebook, HTML/JS, filesystem, network or remote Artifact execution authority was added.

## 24. Accessibility / Browser / Platform Claims
Accessibility engineering target and tested browser set may be stated; formal certification and universal platform/browser claims are prohibited.

## 25. Release Gap Registry
Three classified rows: two nonblocking limitations and one planned Phase 13-2 evidence gap; unclassified rows `0`.

## 26. Release Blockers
`RELEASE_BLOCKERS = 0`; `RELEASE_CRITICAL_INTEGRATION_GAPS = 0`.

## 27. Nonblocking Limitations
Two grouped nonblocking release-gap records remain disclosure-owned; the seven-demo execution evidence gap is P2 and owned by 13-2.

## 28. Seven Demo Registry
Exactly seven `REAL_USER_ENTRY_E2E` contracts are sealed; extra `0`, missing `0`, executed `0`, PASS claims `0`.

## 29. Demo 1 Contract
Dataset Intelligence + Composition Space, retained checksummed tabular fixture, natural-language entry, real Runtime/persistence.

## 30. Demo 2 Contract
Materials ML with retained checksummed dataset fixture and persisted model/evaluation products.

## 31. Demo 3 Contract
Structure + coordination + local environment + polyhedra + experimental XRD with retained structure/XRD fixtures.

## 32. Demo 4 Contract
Trajectory + RDF + MSD + diffusion with retained boundary-aware trajectory fixture.

## 33. Demo 5 Contract
Phonon + Brillouin Zone with retained phonon/structure fixtures and explicit mapping boundaries.

## 34. Demo 6 Contract
Volumetric with retained checksummed grid fixture and presentation-only WebGL authority.

## 35. Demo 7 Contract
Electronic Band + DOS with supplied electronic fixtures; no DFT/GW platform claim.

## 36. Real User Simulation Contract
Normal flow uses user-facing UI, roles, accessible names and visible semantics; internal identities are read only after flow for lineage audit.

## 37. Canonical Scientist Persona
Supported data, reasonable scientific question, no Tool-ID knowledge, result plus limitations expected.

## 38. Imperfect / Exploratory Persona
Ambiguity, limited/unsupported data, back navigation, refresh/recovery, partial execution and limitation inspection are required.

## 39. Negative Path Registry
Ambiguous Intent, unsupported capability/input, partial execution, stale recovery, provider failure and limitation-bearing Report are sealed.

## 40. No-Handcrafted-Injection Policy
Plan, Job, ToolCall, Artifact, Workspace, Finding, Evidence, Report and Recipe injection counts are all zero.

## 41. Persistence / Runtime Requirements
Real PostgreSQL, Redis, MinIO, queue/worker Runtime, registered Adapter execution, persisted Artifact and Workspace-from-real-Job are mandatory.

## 42. Provider Mode Requirements
Deterministic provider replay is release authority; one future bounded live case allows at most two calls, 60-second timeout and zero retries.

## 43. Fixture Registry
Eleven retained fixture records cover all seven demos; missing `0`, checksum mismatch `0`, external downloads `0`.

## 44. Fixture License / Checksum Integrity
Fixtures retain repository provenance/license dispositions and cross-platform-stable text checksums; binary checksums remain byte-exact.

## 45. Natural-Language Prompt Registry
Each demo has one canonical user prompt and one bounded paraphrase without Tool IDs or schema syntax.

## 46. Clarification Expectations
Applicable clarification is user-visible, bounded to two rounds and cannot be bypassed by resolved-Intent injection.

## 47. Eligibility Expectations
Tests assert capability family and acceptable Registry outcomes; they do not pass Tool IDs directly.

## 48. Plan Expectations
Required semantic steps accept AnalysisPlan `0.1/0.2`; handcrafted Plan injection is prohibited.

## 49. Artifact / Workspace Expectations
Exact Artifact kinds and lineage drive one Workspace per real Job; filename, display label, array position and latest-binding authority remain zero.

## 50. Interpretation / Finding Expectations
Grounded interpretation and Finding/Evidence are required only where current persisted contracts apply.

## 51. Report / Recipe Expectations
Reports compose persisted facts; Recipes are exact declarative manifests with execution authority `NONE`.

## 52. Phase 13 Acceptance Registry
Fifty-six unique IDs are sealed, eight per Phase 13-0 through 13-6; `P13X0-A01..A08 = 8/8`.

## 53. Phase 13 Evidence Contract
User-entry, Profile, Intent, Plan, Runtime, Artifact, Workspace, evidence, identity, persistence and presentation axes remain independent.

## 54. Phase 13 Lifecycle Contract
Implementation exact-SHA CI is required; completion and archive are direct pushes without separate CI waits; failed candidates are retained.

## 55. Initial Release Fact Model
`SEALED`; semantic hash `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`.

## 56. Initial Release Scope Baseline
`SEALED`; semantic hash `8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde`.

## 57. Baseline Determinism
PASS locally and in Linux CI after canonical JSON hashing and normalized text-fixture identity.

## 58. Release Scope Drift Audit
`NONE`; capability, validation, input support, scientific semantics and public claims received zero promotion.

## 59. Phase 13-1 Handoff
`ZERO_GAP_VERIFICATION_CLOSURE`; reviewer-gated, no executable task created.

## 60. Phase 13-2 Contract Preview
Contract ready `YES`; execution ready and demo PASS remain `NO` until the Phase 13-1 reviewer gate.

## 61. Backend Baseline Regression
Local full suite: `1320 passed`, 50 service-marked skips; implementation CI Unit Tests PASS.

## 62. Frontend Baseline Regression
`455 passed`; no frontend production behavior changed.

## 63. Typecheck / Build / Lock / Diff
Typecheck, production build, `uv lock --check` and `git diff --check` PASS; lockfile changes `0`.

## 64. Service Integration
PostgreSQL + Redis + MinIO required integration job PASS with zero skipped service tests in CI.

## 65. Linux / Windows Replay
Both sealed invariant replay jobs PASS.

## 66. Browser Smoke
Chromium, Firefox, WebKit and `390x844` retained matrix PASS; seven Phase 13 demos were not executed.

## 67. Security / Secret Scan
Security and secret scan PASS; external downloads, external scientific APIs and real LLM calls `0`.

## 68. Evidence Manifest
41 deterministic members; missing `0`, extra `0`, hash mismatch `0`, unclassified `0`; implementation CI `31451202923 PASS`.

## 69. Files Changed
Only docs, persistent state, TASK queue, audit generator/tests and CI evidence placement changed; production source and lockfiles did not.

## 70. Implementation/Audit Commit
Authoritative implementation: `6217d042d0190c43144e402e4479aa9810b8e9d0`.

## 71. Implementation Exact-SHA CI
Run `31451202923` PASS: Unit, Frontend/browser/build, PostgreSQL/Redis/MinIO, Linux replay and Windows replay all success.

## 72. Failed Candidates
`c26815289b239c1169b344ac02707cd737b0b9e5` / `31449685832`: platform-specific CRLF/LF semantic hash. `0692864ff3981b0e2ee75d5ac88ee2a438da90b6` / `31450249072`: Python audit generator incorrectly placed in Node-only frontend job. Both are historical-only and fixed forward.

## 73. Completion Record
`COMPLETION_RECORDED`; this commit is pushed directly without waiting for completion-record CI.

## 74. Queue Archive
The next direct commit removes only the completed Phase 13-0 task; no archive CI wait is authorized.

## 75. Queue State
After archive: `TASK_BLOCK_COUNT = 0`; Phase 13-1 and Phase 13-2 executable tasks absent.

## 76. Phase 13-1 Reviewer Gate
`REVIEWER_GATE / AWAITING REVIEWER PROMPT`; blocker count `0`, critical integration-gap count `0`.

## 77. Final Repository State
After direct archive push: master, HEAD equals origin/master, clean worktree, Initial Release not complete, Phase 14 absent.

```text
PHASE_13_0 = PASS
PHASE_13 = IN_PROGRESS / RELEASE_SCOPE_SEALED
INITIAL_RELEASE_FACT_MODEL = SEALED
INITIAL_RELEASE_SCOPE_BASELINE = SEALED
INITIAL_RELEASE_SCOPE_BASELINE_DETERMINISM = PASS
INITIAL_RELEASE_SCOPE_BASELINE_HASH = 8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde
REGISTRY = 62
DATAPROFILE = 2.4
MIGRATION = 0007_phase10m1_workspace_domain
PHASE12_PRODUCT_EXPERIENCE_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
PHASE12_BASELINE_MUTATION_BY_13_0 = 0
PHASE13_0_PRODUCTION_CODE_CHANGES = 0
PHASE13_0_BACKEND_BEHAVIOR_CHANGES = 0
PHASE13_0_FRONTEND_BEHAVIOR_CHANGES = 0
PHASE13_0_SCIENTIFIC_BEHAVIOR_CHANGES = 0
PHASE13_0_NEW_SCIENTIFIC_TOOLS = 0
PHASE13_0_NEW_SCIENTIFIC_ALGORITHMS = 0
PHASE13_0_NEW_ARTIFACT_FAMILIES = 0
PHASE13_0_NEW_DATAPROFILE_VERSION = 0
PHASE13_0_NEW_ANALYSISPLAN_VERSION = 0
PHASE13_0_NEW_DATABASE_MIGRATIONS = 0
PHASE13_0_NEW_PUBLIC_API_FAMILIES = 0
PHASE13_0_NEW_DEPENDENCIES = 0
PHASE13_0_LOCKFILE_CHANGES = 0
PHASE13_0_NEW_LLM_CALL_SITES = 0
PHASE13_0_REAL_LLM_CALLS = 0
PHASE13_0_FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
REGISTRY_BEFORE_13_0 = 62
REGISTRY_AFTER_13_0 = 62
DATAPROFILE_BEFORE_13_0 = 2.4
DATAPROFILE_AFTER_13_0 = 2.4
MIGRATION_BEFORE_13_0 = 0007_phase10m1_workspace_domain
MIGRATION_AFTER_13_0 = 0007_phase10m1_workspace_domain
V4_BEFORE_13_0 = 0
V4_AFTER_13_0 = 0
INITIAL_RELEASE_CAPABILITY_MATRIX = SEALED
INITIAL_RELEASE_CLAIM_REGISTRY = SEALED
INITIAL_RELEASE_LIMITATION_REGISTRY = SEALED
INITIAL_RELEASE_FUTURE_SCOPE_REGISTRY = SEALED
INITIAL_RELEASE_NOT_PLANNED_REGISTRY = SEALED
PHASE13_RELEASE_GAP_REGISTRY = SEALED
PHASE13_SEVEN_DEMO_REGISTRY = SEALED
PHASE13_ACCEPTANCE_REGISTRY = SEALED
PHASE13_DEMO_FAMILIES = 7
REAL_USER_ENTRY_E2E_REQUIRED = YES
HANDCRAFTED_PLAN_INJECTION = 0
HANDCRAFTED_JOB_INJECTION = 0
HANDCRAFTED_TOOLCALL_INJECTION = 0
HANDCRAFTED_ARTIFACT_INJECTION = 0
HANDCRAFTED_WORKSPACE_INJECTION = 0
HANDCRAFTED_FINDING_INJECTION = 0
HANDCRAFTED_EVIDENCE_INJECTION = 0
HANDCRAFTED_REPORT_INJECTION = 0
HANDCRAFTED_RECIPE_INJECTION = 0
REAL_PERSISTENCE_REQUIRED = YES
REAL_RUNTIME_REQUIRED = YES
REGISTERED_ADAPTER_EXECUTION_REQUIRED = YES
WORKSPACE_FROM_REAL_JOB_REQUIRED = YES
REPORT_FROM_REAL_PERSISTED_FACTS_REQUIRED = YES
CANONICAL_SCIENTIST_PERSONA = SEALED
IMPERFECT_EXPLORATORY_PERSONA = SEALED
NEGATIVE_PATH_REGISTRY = SEALED
NATURAL_LANGUAGE_ENTRY_REQUIRED = YES_WHERE_PRODUCT_CONTRACT_APPLIES
RELEASE_BLOCKERS = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
NONBLOCKING_LIMITATIONS = 2
UNCLASSIFIED_RELEASE_GAPS = 0
PHASE13_2_DEMOS_EXECUTED = 0
PHASE13_2_DEMO_PASS_CLAIMS = 0
SUPPORTED_EQUALS_VALIDATED = NO
E2E_PASS_EQUALS_REFERENCE_VALIDATED = NO
REPORT_INCLUDED_EQUALS_VALIDATED = NO
RECIPE_EXISTS_EQUALS_REPRODUCIBILITY_VALIDATED = NO
BROWSER_PASS_EQUALS_SCIENTIFIC_PASS = NO
SERVICE_PASS_EQUALS_SCIENTIFIC_PASS = NO
ACCESSIBILITY_PASS_EQUALS_SCIENTIFIC_PASS = NO
FRONTEND_SCIENTIFIC_AUTHORITY = NONE
SCREENSHOT_NUMERIC_SCIENTIFIC_AUTHORITY = NONE
P13X0_ACCEPTANCE = 8/8
PHASE13_ACCEPTANCE_REGISTRY_EXPECTED_TOTAL = 56
IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
COMPLETION_RECORDED
INITIAL_RELEASE_COMPLETE = NO
PHASE_13_1 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_1_EXECUTABLE_TASK_CREATED = NO
PHASE13_2_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
```
# Phase 13-0 Clarification Round-Limit Fact Alignment Correction Addendum

## 1. Conclusion

`PASS / FINAL_FACTS_ALIGNED / INITIAL_RELEASE_SCOPE_SEALED / FACT_ALIGNMENT_CORRECTED`.
This append-only fix-forward corrects only the Phase 13 release-contract projection.
Production AnalysisIntent behavior was already correct and was not changed.

## 2. Baseline And Authority

- Archived Phase 13-0 baseline: implementation `6217d042d0190c43144e402e4479aa9810b8e9d0`, CI `31451202923` PASS, completion `0af74ff078e1dab6324852a8329cea42bf092acb`, archive `7a554cd91b0638898bfe097972f29a097540b514`.
- Production authority: AnalysisIntent `1.0`, `MAX_CLARIFICATION_ROUNDS=1`, `MAX_CLARIFICATION_QUESTIONS=3`, second attempt typed `CLARIFICATION_NOT_ALLOWED`.
- The historical Phase 13-0 statement remains intact and is superseded by this addendum.

## 3. Correction And Occurrence Audit

All seven canonical demo contracts, the Phase 13-2 preview, acceptance wording,
real-user contract, scope, fact-model documentation and 13-1 handoff now inherit
the one-round production authority. Current canonical two-round assertions are zero;
remaining mentions are classified historical or correction/governance evidence.

## 4. Hash Impact

- `OLD_INITIAL_RELEASE_FACT_MODEL_HASH=e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`
- `FACT_MODEL_HASH_IMPACT=NO`
- `CURRENT_INITIAL_RELEASE_FACT_MODEL_HASH=e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`
- Reason: clarification fields are outside the Fact Model semantic hash dependency domain; the model references the demo registry by path.
- `OLD_INITIAL_RELEASE_SCOPE_BASELINE_HASH=8e8b4f659888635192d259eee90f3befdd655cacb292a78c5e13c20a5fdabdde`
- `SCOPE_BASELINE_HASH_IMPACT=YES`
- `CURRENT_INITIAL_RELEASE_SCOPE_BASELINE_HASH=93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627`
- Reason: the Scope Baseline hashes the seven-demo registry content. The old hash is historical and superseded.
- Two generator runs and Linux/Windows CI replay produced identical current semantic hashes.

## 5. Governance And Scientific Boundaries

`ONE_ROUND_CLARIFICATION_SUCCESS=PASS`, `SECOND_ROUND_TYPED_FAILURE=PASS`,
`MAX_THREE_QUESTIONS=PASS`, and `RESOLVED_INTENT_BYPASS=0`. Seven demo families
remain sealed but unexecuted. Release blockers and release-critical integration
gaps remain zero. Registry 62, DataProfile 2.4, EligibilityResolution 1.0,
AnalysisPlan 0.1/0.2 and migration `0007_phase10m1_workspace_domain` are unchanged.

No production code, production behavior, scientific behavior, Tool, algorithm,
Artifact family, schema version, migration, API, dependency, lockfile, LLM call
site, real LLM call, external download, or frontend scientific recomputation was added.

## 6. Verification

- Local backend: `1327 passed, 50 skipped`.
- Frontend: `455 passed`; typecheck and production build PASS.
- Focused correction/governance compatibility: `82 passed`; correction suite `7 passed`.
- `uv lock --check`, `git diff --check`, docs link check and secret scan PASS.
- Linux/Windows semantic hash replay, PostgreSQL/Redis/MinIO, Chromium, Firefox,
  WebKit and Chromium `390x844`: PASS in exact-SHA CI `31455125693`.

## 7. Lifecycle And Queue

- Correction implementation: `abe4bd68363f9eb9c357a840b17d0f2c216ebfee`.
- Implementation exact-SHA CI: `31455125693` PASS.
- `CORRECTION_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI`.
- Completion is recorded by the commit containing this addendum; no completion CI wait is required.
- Phase 13-1 remains `REVIEWER_GATE / ZERO_GAP_VERIFICATION_CLOSURE / AWAITING REVIEWER PROMPT`.
- Phase 13-2 is not queued or executable; Initial Release is not complete; Phase 14 is not created.

## 8. Required Status

```text
PHASE_13_0_FACT_CORRECTION = PASS
CORRECTION_TYPE = FACT_ALIGNMENT_FIX_FORWARD
PHASE13_CLARIFICATION_MAX_ROUNDS = 1
PHASE13_CLARIFICATION_MAX_QUESTIONS = 3
PHASE13_SECOND_CLARIFICATION_ROUND = TYPED_FAILURE
CURRENT_CANONICAL_TWO_ROUND_ASSERTIONS = 0
PRODUCTION_CODE_CHANGES = 0
PRODUCTION_BEHAVIOR_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
FACT_MODEL_HASH_IMPACT = NO
INITIAL_RELEASE_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
SCOPE_BASELINE_HASH_IMPACT = YES
INITIAL_RELEASE_SCOPE_BASELINE_HASH = 93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627
BASELINE_DETERMINISM = PASS
RELEASE_BLOCKERS = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
P13X0_ACCEPTANCE = 8/8
PHASE13_DEMO_FAMILIES = 7
PHASE13_2_DEMOS_EXECUTED = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
PHASE_13_0 = PASS / FINAL_FACTS_ALIGNED / INITIAL_RELEASE_SCOPE_SEALED / FACT_ALIGNMENT_CORRECTED
PHASE_13_1 = REVIEWER_GATE / ZERO_GAP_VERIFICATION_CLOSURE / AWAITING REVIEWER PROMPT
PHASE13_1_EXECUTABLE_TASK_CREATED = NO
PHASE13_2_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 13-2 Seven Canonical Real-User E2E Demonstrations Result

## Conclusion

Status: `FAILED / BLOCKED_BY_RELEASE_CRITICAL_INTEGRATION_DEFECTS`.

Phase 13-1 authority, both Phase 13 hashes, 11 fixture identities, all seven
demo contracts and the no-injection policy resolved. Deterministic current-code
probes then found three P0 product-entry defects before any real Job could be
created. Phase 13-2 therefore cannot honestly satisfy its seven-demo PASS gate.
No production or scientific change was made, and no demonstration PASS is
claimed.

## Entry And Attempts

- Entry HEAD/origin: `d07c8809e677049bcf651c1aa63ab04fddec1ec2`; branch `master`; clean worktree.
- Phase 13-1 implementation: `d1a60955a77aec000f1e6fd630f0770db545421d`;
  exact-SHA CI `31460352586` PASS; completion `3d9c59b`; archive `d07c8809`.
- Fact Model hash: `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`.
- Scope baseline hash: `93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627`.
- Current parser, DataProfile builder, AnalysisIntent, Eligibility and Planner
  were probed using every sealed fixture and canonical/alternate prompt.
- Local PostgreSQL and Redis endpoints, MinIO binary, Playwright and bounded
  DeepSeek configuration were inspected. Execution stopped before provider,
  service-backed queue/runtime and browser acceptance because the product entry
  contract had already failed.

## Release Findings

- `P13-RF-001` P0: schema/parser produce DataProfile 2.3/2.4, but Planner accepts
  only 2.0/2.1 (`PROFILE_2_REQUIRED`), blocking demos 4 and 7.
- `P13-RF-002` P0: the sealed experimental XRD JSON is parser-unsupported and
  eligibility reports `XRD_COMPARISON_SOURCE_NOT_ELIGIBLE`, blocking demo 3.
- `P13-RF-003` P0: both sealed phonon/BZ prompts return `INTENT_UNSUPPORTED`,
  blocking demo 5.
- `P13-RF-004` P1: the volumetric canonical prompt fails while its bounded
  alternate reaches `structure.volumetric_data`, requiring contract correction.

## Verification

- `uv run python scripts/generate_phase13_2_blocker_evidence.py`: PASS.
- Focused Phase 13 governance tests: `26 passed`.
- Full backend regression: `1339 passed, 50 skipped`.
- Frontend regression: `455 passed`; typecheck and production build PASS.
- `uv lock --check` and `git diff --check`: PASS.
- Production files changed: `0`; scientific files changed: `0`; dependencies,
  lockfile, database, migration, public API and Registry changes: `0`.
- Live LLM calls: `0`; external downloads: `0`; handcrafted injections: `0`.

## Status Markers

```text
PHASE_13_2 = FAILED / BLOCKED_BY_RELEASE_CRITICAL_INTEGRATION_DEFECTS
PHASE13_DEMO_FAMILIES = 7
PHASE13_2_DEMOS_EXECUTED = 0
PHASE13_2_DEMO_PASS_CLAIMS = 0
P13X2_ACCEPTANCE = 0/8
RELEASE_CRITICAL_INTEGRATION_DEFECTS = 3
DOCUMENTATION_DEFECTS = 1
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
HANDCRAFTED_PLAN_INJECTION = 0
HANDCRAFTED_JOB_INJECTION = 0
HANDCRAFTED_TOOLCALL_INJECTION = 0
HANDCRAFTED_ARTIFACT_INJECTION = 0
HANDCRAFTED_WORKSPACE_INJECTION = 0
HANDCRAFTED_FINDING_INJECTION = 0
HANDCRAFTED_EVIDENCE_INJECTION = 0
HANDCRAFTED_REPORT_INJECTION = 0
HANDCRAFTED_RECIPE_INJECTION = 0
PHASE13_2_PRODUCTION_CODE_CHANGES = 0
PHASE13_2_SCIENTIFIC_BEHAVIOR_CHANGES = 0
REGISTRY = 62
DATAPROFILE = 2.4
MIGRATION = 0007_phase10m1_workspace_domain
INITIAL_RELEASE_COMPLETE = NO
PHASE_13_3_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
TASK_BLOCK_COUNT = 1
REVIEWER_ACTION_REQUIRED = YES
```

# Phase 13-1 Release-Critical Product-Entry Fix-Forward Result

## 1. Conclusion

Status: `PASS / REOPENED_FIX_FORWARD / RELEASE_CRITICAL_PRODUCT_ENTRY_GAPS_CLOSED / CANONICAL_ENTRY_SLICE_7_OF_7_READY`. Historical Phase 13-1 zero-gap verification remains forensic truth but is superseded for current release authority by the stronger Phase 13-2 real-entry evidence.

## 2. Triggering Phase 13-2 Failure

Historical evidence implementation `456b698948d286d4e60dc8d6807748a97df9fb96`, CI `31482829487` PASS, retained `P13-RF-001..004`, three release-critical defects, one documentation defect, zero scientific/security defects and zero full demos executed.

## 3. Historical Authority

Original Phase 13-1 implementation `d1a60955a77aec000f1e6fd630f0770db545421d` / CI `31460352586` remains `PASS_AT_TIME`; original Phase 13-2 remains `FAILED_HISTORICAL` and its evidence was not rewritten.

## 4. Entry Gate And Queue

Entry was clean `master` at `456b698...`; one failed retained Phase 13-2 block was preserved and one fix-forward task was admitted. No rerun task was created.

## 5. Current Fact And Scope Baselines

Fact Model hash remains `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06` (`IMPACT=NO`). Scope hash `caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4` supersedes historical `93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627` (`IMPACT=YES`, deterministic Linux/Windows canonical JSON).

## 6. RF-001 Root Cause, Fix And Regression

Global Planner/interpretation gates duplicated stale `2.0/2.1` rules. One explicit shared allowlist accepts existing `2.0..2.4`, rejects future `2.5+`, and is projected exactly to PlannerWorkbench. Demo 4 profile 2.3 and Demo 7 profile 2.4 now plan successfully; stale hashes remain rejected.

## 7. RF-002 XRD Authority Decision And Resolution

Decision: `Branch B1`. The old `perfect_match.json` is an expected-result record, not user input. Demo 3 now uses the existing strict `phase10n3.experimental_xrd_resource.v1` supported-with-limits contract. Generic JSON/phonon upload support was not promoted; exact resource identity and existing XRD comparison eligibility are preserved.

## 8. RF-003 Intent Coverage

Bounded semantic mapping now recognizes supplied phonon Band/DOS plus Structure-backed Brillouin-zone context without Tool IDs or exact-prompt branches. Canonical and alternate prompts reach the intended existing Tool family; DFT phonon generation, advanced unsupported requests and unrelated substring controls remain unsupported.

## 9. RF-004 Authority Decision

Decision: `Branch B`. The old canonical wording overstated structure context; the corrected natural-language prompt asks only for supported supplied-grid slice/volume views. Canonical and alternate prompts reach `structure.volumetric_data`; Bader/topology remains Future Scope.

## 10. Finding Closure Registry

`P13-RF-001 = CLOSED_WITH_REGRESSION`; `P13-RF-002 = CLOSED_WITH_AUTHORITY_PRESERVED`; `P13-RF-003 = CLOSED_WITH_REGRESSION`; `P13-RF-004 = CLOSED`. Original severity, evidence and failure SHA remain retained with append-only closure provenance.

## 11. Canonical Product Entry Slice

Level C is exact retained fixture -> production parser or approved normalized mapper -> DataProfile -> natural-language AnalysisIntent -> bounded clarification -> Eligibility -> capability Planner -> PlanValidator -> stop before Job. Levels A/B/C PASS; Level D remains Phase 13-2.

## 12. Demo Entry Slices

Demo 1 Dataset/Composition, Demo 2 Materials ML, Demo 3 Structure/XRD, Demo 4 Trajectory analytics, Demo 5 Phonon/BZ, Demo 6 Volumetric and Demo 7 Electronic Band/DOS are `7/7 READY` and `7/7 PLAN_VALIDATED`, with zero blocked or wrong-capability results.

## 13. Negative Entry Slice And No Injection

Future Bader, unsupported input, stale Profile hash, missing resource binding and second clarification round produce typed non-ready outcomes and no Plan. Handcrafted Intent, Eligibility, Plan and Tool selection are all zero; production contains no phase/demo fixture/checksum or exact-prompt routing authority.

## 14. Release Gap And Input-Support Reconciliation

Release-critical integration gaps: `3 -> 0`; documentation defects: `1 -> 0`; scientific/security/unclassified gaps: `0`. Input-support promotions and scientific validation/V4 promotions are zero.

## 15. Scientific Authority Non-Change

Registry `62`, DataProfile `2.4`, AnalysisIntent `1.0`, EligibilityResolution `1.0`, AnalysisPlan `0.1/0.2`, migration `0007_phase10m1_workspace_domain`. No Tool, algorithm, Adapter science, Artifact family, schema version, database, API family, dependency, provider, LLM call site or frontend scientific recomputation changed.

## 16. Verification

Backend `1351 passed, 50 skipped`; frontend `456 passed`; Phase 13 governance `37 passed`; final focused fix-forward/history `16 passed`; PlannerWorkbench `32 passed`; typecheck, build, `uv lock --check`, `git diff --check`, hash determinism, manifest and secret scan PASS. npm audit is `UNAVAILABLE` because the configured mirror returns `[NOT_IMPLEMENTED]`.

## 17. Services, Browser And Platform

Exact-SHA CI passed PostgreSQL/Redis/MinIO, Chromium/Firefox/WebKit and 390x844 retained browser evidence, production build, Linux/Windows sealed replay and cross-platform fix-forward hash comparison.

## 18. Implementation And CI

Implementation SHA `2e47263ac3042663cf901a7fcb8f44e203143e2e`; exact-SHA CI `31493208538` success. Failed remediation candidates: none. Completion is recorded in the following direct commit; queue archive follows separately without CI wait.

## 19. Phase 13-2 Rerun Handoff

The corrected seven contracts, fixture registry, prompts, 7/7 entry results, negative controls, no-injection rules, current hashes and real persistence/runtime requirements are sealed. Phase 13-2 has not been rerun; `P13X2_ACCEPTANCE = 0/8`; a separate reviewer prompt is required.

## 20. Required Markers

```text
PHASE_13_1_FIX_FORWARD = PASS
REMEDIATION_TRIGGER = PHASE13_2_REAL_USER_ENTRY_FAILURE
P13_RF_001 = CLOSED
P13_RF_002 = CLOSED
P13_RF_003 = CLOSED
P13_RF_004 = CLOSED
PROFILE_PLANNER_COMPATIBILITY_DRIFT = CLOSED
XRD_INPUT_AUTHORITY_RESOLVED = YES
INPUT_SUPPORT_PROMOTIONS = 0
PHONON_BZ_INTENT_COVERAGE = PASS
VOLUMETRIC_CANONICAL_PROMPT = ALIGNED
CANONICAL_PRODUCT_ENTRY_SLICE_GATE = PASS
CANONICAL_ENTRY_SLICE_READY = 7/7
CANONICAL_ENTRY_SLICE_BLOCKED = 0
CANONICAL_ENTRY_SLICE_WRONG_CAPABILITY = 0
ENTRY_SLICE_JOB_CREATION = 0
ENTRY_SLICE_QUEUE_MESSAGES = 0
ENTRY_SLICE_TOOLCALL_CREATION = 0
ENTRY_SLICE_ARTIFACT_CREATION = 0
HANDCRAFTED_INTENT_INJECTION = 0
HANDCRAFTED_ELIGIBILITY_INJECTION = 0
HANDCRAFTED_PLAN_INJECTION = 0
HANDCRAFTED_TOOL_SELECTION = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
DOCUMENTATION_DEFECTS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
UNCLASSIFIED_RELEASE_GAPS = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
PHASE13_CLARIFICATION_MAX_ROUNDS = 1
PHASE13_CLARIFICATION_MAX_QUESTIONS = 3
PHASE13_SECOND_CLARIFICATION_ROUND = TYPED_FAILURE
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
SCIENTIFIC_ADAPTER_BEHAVIOR_CHANGES = 0
NEW_ARTIFACT_FAMILIES = 0
SCIENTIFIC_VALIDATION_PROMOTIONS = 0
V4_PROMOTIONS = 0
FRONTEND_SCIENTIFIC_RECOMPUTATION = 0
NEW_DATAPROFILE_VERSION = 0
NEW_ANALYSISINTENT_VERSION = 0
NEW_ELIGIBILITY_VERSION = 0
NEW_ANALYSISPLAN_VERSION = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_PUBLIC_API_FAMILIES = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
OLD_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
FACT_MODEL_HASH_IMPACT = NO
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
OLD_SCOPE_BASELINE_HASH = 93dea4a2b0bf31215ab2af1952b16ac47b20b7ed9b111bb2fb60ef70dd431627
SCOPE_BASELINE_HASH_IMPACT = YES
CURRENT_SCOPE_BASELINE_HASH = caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4
BASELINE_DETERMINISM = PASS
PHASE13_2_FULL_E2E_RERUN = NO
PHASE13_2_DEMOS_EXECUTED = 0
PHASE13_2_DEMO_PASS_CLAIMS = 0
P13X2_ACCEPTANCE = 0/8
PHASE13_2_RERUN_REQUIRED = YES
PHASE13_2_RERUN_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
FIX_FORWARD_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
FIX_FORWARD_COMPLETION_RECORDED
FIX_FORWARD_QUEUE_ARCHIVED
```

## 21. Direct Queue Archive Addendum

The completed Phase 13-1 fix-forward block is removed in the direct archive
commit containing this addendum. The historical failed Phase 13-2 block remains
the sole TASK block. No archive-CI verification claim is made.

```text
FAILED_RETAINED_TASK_BLOCKS = 1
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 1
PHASE13_2_RERUN_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
FIX_FORWARD_QUEUE_ARCHIVED
```
# Phase 13-2 Seven Canonical Real-User E2E Full Rerun Result

## Conclusion

`FAILED_RERUN / REVIEWER_ACTION_REQUIRED`.

Attempt 1 remains `FAILED_HISTORICAL / BLOCKED_BY_PRODUCT_ENTRY_DEFECTS`.
Phase 13-1 Fix-Forward remains PASS. Attempt 2 passed its remediation, hash and
entry gates, then stopped during a fresh seven-family production-runtime
preflight after three new P0 release-critical integration defects were observed.
No production fix was made and no full demo PASS is claimed.

## Findings

- `P13-RR-001`: Demo 5 parsed `PhononBand`/`PhononDos` exact IDs are absent from
  the production object store; registered phonon Adapters fail `Unknown input ref`.
- `P13-RR-002`: Demo 7 parsed `ElectronicBand`/`ElectronicDos` exact IDs are
  absent from the production object store; registered electronic Adapters fail
  `Unknown input ref`.
- `P13-RR-003`: Demo 3's real experimental XRD comparison rejects the real
  theoretical dependency because their wavelengths are incompatible.

All three are product integration defects. Scientific defects and security
defects remain zero.

## Execution And Authority

- Fresh runtime preflights: `7/7`.
- Full service-backed real-user demos executed: `0/7`.
- Demo PASS or explicit-limit claims: `0/7`.
- `P13X2_ACCEPTANCE = 0/8`.
- Current Fact Model hash:
  `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`.
- Current Scope Baseline hash:
  `caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4`.
- Registry/DataProfile/Intent/Eligibility/Plan/migration:
  `62 / 2.4 / 1.0 / 1.0 / 0.1+0.2 / 0007_phase10m1_workspace_domain`.
- Production, scientific, schema, API, dependency and provider changes: `0`.

## Verification And Lifecycle

- Focused governance: `21 passed`.
- Backend: `1356 passed, 50 skipped`.
- Frontend: `456 passed`.
- Typecheck/build/lock/diff: PASS.
- Failure evidence implementation:
  `0877450140a76ad7ecd59e99ad48f0c19c5e7059`.
- Implementation exact-SHA CI: `31497337708 / success`.
- CI jobs: Unit, Frontend/browser, Linux replay, Windows replay and
  PostgreSQL/Redis/MinIO integration all success.
- Failed candidates before evidence commit: none. One local backend command
  timed out at 120 seconds and passed when rerun with a 300-second limit.
- Completed at: `2026-08-11 21:55:28 +08:00`.

The original failed attempt evidence, remediation evidence and attempt-2
evidence remain separate. Both failed Phase 13-2 task blocks are retained.
Phase 13-3 is blocked; Initial Release is not complete; Phase 14 is absent.

```text
PHASE_13_2_RERUN = FAILED

PHASE13_2_ATTEMPT_1 = FAILED_HISTORICAL
PHASE13_1_FIX_FORWARD = PASS
PHASE13_2_ATTEMPT_2 = FAILED_RERUN

P13_RR_001 = OPEN_REVIEWER_ACTION_REQUIRED
P13_RR_002 = OPEN_REVIEWER_ACTION_REQUIRED
P13_RR_003 = OPEN_REVIEWER_ACTION_REQUIRED

RELEASE_CRITICAL_INTEGRATION_DEFECTS = 3
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0

PHASE13_DEMO_FAMILIES = 7
FRESH_RUNTIME_PREFLIGHTS = 7/7
PHASE13_2_DEMOS_EXECUTED = 0
DEMO_PASS_OR_EXPLICIT_LIMIT = 0/7
P13X2_ACCEPTANCE = 0/8

OLD_DEMO_RESULT_AS_RERUN_PASS = 0
HANDCRAFTED_INTENT_INJECTION = 0
HANDCRAFTED_ELIGIBILITY_INJECTION = 0
HANDCRAFTED_ANALYSISPLAN_INJECTION = 0
HANDCRAFTED_JOB_INJECTION = 0
HANDCRAFTED_TOOLCALL_INJECTION = 0
HANDCRAFTED_ARTIFACT_INJECTION = 0
HANDCRAFTED_WORKSPACE_INJECTION = 0
HANDCRAFTED_REPORT_INJECTION = 0
HANDCRAFTED_RECIPE_INJECTION = 0

PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_DATAPROFILE_VERSION = 0
NEW_ANALYSISINTENT_VERSION = 0
NEW_ELIGIBILITY_VERSION = 0
NEW_ANALYSISPLAN_VERSION = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_PUBLIC_API_FAMILIES = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
FRONTEND_SCIENTIFIC_RECOMPUTATION = 0

PHASE_13_3 = BLOCKED_BY_PHASE13_2_RERUN
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
FAILED_RETAINED_TASK_BLOCKS = 2
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 2
PHASE14_CREATED = NO
```

# Phase 13-1 Integration Fix-Forward #2 Result

## 1. Conclusion

`PASS / FIX_FORWARD_2 / RUNTIME_RESOURCE_RESOLUTION_CLOSED /
XRD_DEPENDENCY_COMPATIBILITY_CLOSED / CANONICAL_EXECUTION_PREFLIGHT_7_OF_7_READY`.
Phase 13-2 Attempt 3 was not executed or queued.

## 2-6. Trigger, History, Entry Gate, Queue, Baselines

Attempt 1 and Attempt 2 remain immutable failed history. Fix-Forward #1 remains
PASS. Entry was clean on `master` with two retained failed TASK blocks. Fact
Model remains `e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06`.
Scope Baseline `eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94`
supersedes `caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4`.

## 7-14. RR-001 and RR-002

Both findings shared one root cause: parsed `PhononBand`, `PhononDos`,
`ElectronicBand` and `ElectronicDos` exact IDs escaped the canonical Runtime
source-resource index and durable resolver. One bounded generic registration
mechanism now preserves exact ID, type, hash and dataset scope in immediate and
PostgreSQL/MinIO-backed resolution. Missing ID, wrong project, hash mismatch,
stale identity and wrong subtype remain rejected. Electronic spin, k-point,
band/path, DOS channel and energy-unit provenance are unchanged.

## 15-19. RR-003

Authority decision: Branch B1. `structure.xrd@0.1.0` legally binds the existing
`CuKa` configuration, not arbitrary wavelength. Demo 3's retained experimental
fixture now uses exact `1.54184 angstrom`, matching the approved theoretical
configuration. The strict mismatch case still rejects `1.5406`; no conversion,
reprojection, tolerance, peak-policy or XRD algorithm changed.

## 20-30. Findings and Level C/C2

`P13-RR-001`, `P13-RR-002`, and `P13-RR-003` are closed. Level C is `7/7`.
Level C2 is `7/7`, with eight execution-eligible root kinds audited and eight
Runtime-resolvable. Root-resolution, dependency-contract and scientific-
compatibility failures are all zero. Jobs, queue messages, ToolCalls, produced
Artifacts, Workspaces, Reports and Recipes created by C2 are all zero.

## 31-38. Authority and Hashes

No handcrafted Intent, Eligibility, Plan or Tool selection was used. Release-
critical integration gaps are zero; scientific/security/unclassified defects
are zero. Input support, capability and scientific-validation promotions are
zero. Fact Model impact is `NO`; Scope Baseline impact is `YES` because the
retained Demo 3 checksum changed. Repeated and Linux/Windows hashes are equal.
Phase 11 and Phase 12 authorities are unchanged.

## 39-49. Regression and Evidence

- Backend: `1374 passed, 50 skipped` locally.
- Frontend: `456 passed`; typecheck and build PASS.
- Focused Phase 13 C2/governance: `23 passed`.
- PostgreSQL/Redis/MinIO: `49 passed, 0 skipped` in exact-SHA CI.
- Chromium, Firefox, WebKit and 390x844 retained browser matrix: PASS.
- Linux/Windows invariant replay and semantic hash comparison: PASS.
- `uv lock --check`, `git diff --check`, security, secret scan and manifest: PASS.

## 50-59. Handoff and Lifecycle

Attempt 3 handoff is sealed and requires all seven demos from scratch under a
separate reviewer prompt. Implementation `bc6a6f525515c256c6807c71c5a5f2591607abab`
passed exact-SHA CI `31504920945`. Failed candidate `67a95c4f94088fcd1f8e351f65d617840ccd9906`
/ run `31503729464` is retained; root causes were historical evidence
regeneration and missing integration-test base-table bootstrap. Completion is
recorded here; queue archive follows in a separate direct commit.

```text
PHASE_13_1_FIX_FORWARD_2 = PASS
REMEDIATION_TRIGGER = PHASE13_2_ATTEMPT_2_RUNTIME_PREFLIGHT_FAILURE
P13_RR_001 = CLOSED
P13_RR_002 = CLOSED
P13_RR_003 = CLOSED
PARSED_RESOURCE_PERSISTENCE_AND_RUNTIME_RESOLUTION_GAP = CLOSED
XRD_DEPENDENCY_COMPATIBILITY_GAP = CLOSED
ALL_EXECUTION_ELIGIBLE_ROOT_RESOURCES_RUNTIME_RESOLVABLE = YES
UNRESOLVABLE_EXECUTION_ELIGIBLE_RESOURCE_KINDS = 0
CANONICAL_PRODUCT_ENTRY_SLICE_GATE = PASS
CANONICAL_ENTRY_SLICE_READY = 7/7
CANONICAL_EXECUTION_PREFLIGHT_GATE = PASS
CANONICAL_EXECUTION_PREFLIGHT_READY = 7/7
CANONICAL_EXECUTION_PREFLIGHT_BLOCKED = 0
ROOT_RESOURCE_RESOLUTION_FAILURES = 0
DEPENDENCY_CONTRACT_FAILURES = 0
SCIENTIFIC_COMPATIBILITY_FAILURES = 0
XRD_WAVELENGTH_MISMATCH_REJECTION = UNCHANGED
INPUT_SUPPORT_PROMOTIONS = 0
CAPABILITY_PROMOTIONS = 0
SCIENTIFIC_VALIDATION_PROMOTIONS = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
OLD_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
FACT_MODEL_HASH_IMPACT = NO
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
OLD_SCOPE_BASELINE_HASH = caf9a67d7eb1f966eb3ea477beb60d0111020c84c3d065ed547ce816d9d98fd4
SCOPE_BASELINE_HASH_IMPACT = YES
CURRENT_SCOPE_BASELINE_HASH = eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94
BASELINE_DETERMINISM = PASS
REAL_LLM_CALLS = 0
PHASE13_2_ATTEMPT_3_FULL_E2E = NO
PHASE13_2_DEMOS_EXECUTED = 0
P13X2_ACCEPTANCE = 0/8
FIX_FORWARD_2_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
FIX_FORWARD_2_COMPLETION_RECORDED
PHASE13_2_ATTEMPT_3_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
```

## Phase 13-1 Fix-Forward #2 Queue Archive

Completion commit `eed9af49ce339804b6913c0f3b1fff2cc3e18ee8` was pushed directly
after implementation exact-SHA CI passed. The completed Fix-Forward #2 block
was removed from `TASKS.md`; both historical failed Phase 13-2 blocks remain
unchanged. No Attempt 3, Phase 13-3, or Phase 14 executable task was created.

```text
FIX_FORWARD_2_QUEUE_ARCHIVED
FAILED_RETAINED_TASK_BLOCKS = 2
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 2
PHASE13_2_ATTEMPT_3_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
PHASE14_CREATED = NO
```

# Phase 13-2 Attempt 3 Seven Canonical Real-User E2E Demonstrations Result

## Conclusion and History

`FAILED / REVIEWER_ACTION_REQUIRED`. Attempt 1 remains `FAILED_HISTORICAL`,
Fix-Forward #1 remains PASS, Attempt 2 remains `FAILED_RERUN_HISTORICAL`, and
Fix-Forward #2 remains PASS (`bc6a6f525515c256c6807c71c5a5f2591607abab`,
CI `31504920945`). Attempt 3 passed its repository, authority, Level C 7/7,
Level C2 7/7, eight-of-eight resource and service entry gates, then stopped on
a new P0 during the first fresh Level-D execution. No production repair was made.

## Fresh Execution and Finding

Demo 1 used a fresh HTTP `/datasets/upload`, retained `formulas.csv`, DataProfile
2.4, canonical natural-language prompt, AnalysisIntent 1.0, EligibilityResolution
1.0, capability Planner, PlanValidator, persisted Plan/Job and real Redis enqueue.
A newly constructed production QueueWorkerRuntime failed before ToolCall creation:

```text
TOOL_INPUT_INVALID: Unknown input ref: profile
```

`P13-R3-001` is a P0 `RELEASE_CRITICAL_INTEGRATION_DEFECT`. The upload process
contains normalized source exports, but Planner's SQL dataset lacks
`normalizedExports`; the fresh PostgreSQL/MinIO durable resolver cannot rebuild
the exact source object store. Fix-Forward #2 C2 manually persisted those exports
and did not cover the real endpoint-to-worker boundary.

Demo 1 is `FAIL_PRODUCT_INTEGRATION`; Demo 2-7 are
`NOT_EXECUTED_AFTER_P0_STOP`. Negative paths, browser-driven Attempt 3 flows,
mobile inspection and bounded live DeepSeek were not executed. Full demos are
`0/7`, old evidence reused as PASS is 0, and `P13X2_ACCEPTANCE = 0/8`.

## Authority, Regression and Lifecycle

All handcrafted injection and Runtime fallback counters are zero. No ToolCall,
Artifact, Workspace, interpretation, Finding/Evidence, Report or Recipe was
created. Registry 62, DataProfile 2.4, AnalysisIntent 1.0, EligibilityResolution
1.0, AnalysisPlan 0.1/0.2, migration 0007, Fact Model
`e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06` and
Scope Baseline `eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94`
are unchanged.

- Evidence governance: `4 passed`.
- Service reproduction: `1 passed, 0 skipped` locally.
- Backend: `1378 passed, 52 skipped`; frontend: `456 passed`.
- Typecheck, build, lock, diff, deterministic manifest, security and secret scan: PASS.
- Evidence SHA: `fc54d4eec3f537e1ad57fca8d085539e9acd1ac3`.
- Exact-SHA CI: `31511289851` PASS, including 50 zero-skip service tests,
  retained browser gates and Linux/Windows replay.
- Completion/archive SHA: not applicable; Attempt 3 failed and all three failed
  Phase 13-2 task blocks remain retained.

```text
PHASE_13_2_ATTEMPT_3 = FAILED / REVIEWER_ACTION_REQUIRED
DEMO_1_STATUS = FAIL_PRODUCT_INTEGRATION
DEMO_2_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_3_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_4_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_5_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_6_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_7_STATUS = NOT_EXECUTED_AFTER_P0_STOP
PHASE13_2_ATTEMPT_3_DEMOS_EXECUTED = 0
OLD_EVIDENCE_REUSED_AS_PASS = 0
P13X2_ACCEPTANCE = 0/8
P13_R3_001 = OPEN_REVIEWER_ACTION_REQUIRED
RELEASE_CRITICAL_INTEGRATION_DEFECTS = 1
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
ALL_HANDCRAFTED_INJECTION_COUNTERS = 0
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
CURRENT_SCOPE_BASELINE_HASH = eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94
FACT_MODEL_HASH_IMPACT_BY_ATTEMPT_3 = NO
SCOPE_BASELINE_HASH_IMPACT_BY_ATTEMPT_3 = NO
BASELINE_DETERMINISM = PASS
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
REAL_LLM_CALLS = 0
PHASE_13_3 = BLOCKED_BY_PHASE13_2_ATTEMPT_3
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
FAILED_RETAINED_TASK_BLOCKS = 3
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 3
PHASE14_CREATED = NO
```

# Phase 13-2 Attempt 4 Seven Canonical Real-User E2E Demonstrations Result

## Conclusion and History

`FAILED / REVIEWER_ACTION_REQUIRED`. Attempts 1-3 remain immutable historical
failures and Fix-Forwards 1-3 remain PASS. Attempt 4 passed repository,
authority, Level C `7/7`, Level C2 `7/7`, and real upload-to-fresh-worker D0
entry gates, then stopped on two new P0 product-integration findings during the
first fresh full demonstration. No production or scientific repair was made.

## Fresh Demo 1 and Findings

Fresh Demo 1 used the current `formulas.csv`, canonical natural-language prompt,
real HTTP upload, PostgreSQL/MinIO durable source authority, AnalysisIntent 1.0,
EligibilityResolution 1.0, capability-aware Planner, PlanValidator, persisted
Job, Redis enqueue, a fresh QueueWorkerRuntime, registered Adapter execution,
four persisted Artifacts, and Workspace projection.

- `P13-R4-001` (`CANONICAL_PROMPT_TO_SEALED_CAPABILITY_MISMATCH`): the actual
  Plan and ToolCall contain only `dataset.materials_explorer`. The sealed Demo 1
  contract also requires `dataset.composition_space`, but no such ToolCall or
  `plotly_json` Artifact was produced.
- `P13-R4-002` (`REAL_USER_REPORT_FINALIZE_BLOCKED_BY_PLAN_0_1_WORKSPACE_POLICY`):
  the Planner-produced AnalysisPlan 0.1 Workspace is `LEGACY_READ_ONLY`; the
  frontend disables Report Finalize for read-only Workspaces. A diagnostic
  direct API finalize was excluded from real-user PASS authority.

Demo 1 is `FAIL_PRODUCT_INTEGRATION`. Demo 2-7, negative scenarios, Attempt 4
browser execution, mobile inspection, and bounded live DeepSeek were not
executed after the P0 stop. Fresh demos started are `1/7`, full demos completed
are `0/7`, old evidence reused as PASS is 0, and `P13X2_ACCEPTANCE = 0/8`.

## Regression and Lifecycle

- D0: `1 passed, 0 skipped` using real PostgreSQL, Redis, and MinIO.
- Backend: `1391 passed, 52 skipped`; frontend: `456 passed`.
- Phase 13 focused/governance: `46 passed`.
- Typecheck, build, lock, diff, current Fact/Scope hash, security, secret scan,
  evidence manifest, retained browser gates, and Linux/Windows replay: PASS.
- Local failed test candidate: `1390 passed, 52 skipped, 1 failed`; root cause
  was the Attempt 4 TASK block's English status label. The queue/evidence-only
  correction passed the full rerun.
- Evidence SHA: `9b087606e1d6093e3129dc20e43020790e703a58`.
- Exact-SHA CI: `31577647965` PASS across all five required jobs.
- Completion/archive SHA: not applicable. Attempt 4 failed; all four failed
  Phase 13-2 blocks remain in `TASKS.md`.

```text
PHASE_13_2_ATTEMPT_4 = FAILED / REVIEWER_ACTION_REQUIRED
PHASE13_2_ATTEMPT_1 = FAILED_HISTORICAL
PHASE13_1_FIX_FORWARD_1 = PASS
PHASE13_2_ATTEMPT_2 = FAILED_RERUN_HISTORICAL
PHASE13_1_FIX_FORWARD_2 = PASS
PHASE13_2_ATTEMPT_3 = FAILED_RERUN_HISTORICAL
PHASE13_1_FIX_FORWARD_3 = PASS
DEMO_1_STATUS = FAIL_PRODUCT_INTEGRATION
DEMO_2_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_3_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_4_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_5_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_6_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_7_STATUS = NOT_EXECUTED_AFTER_P0_STOP
PHASE13_2_ATTEMPT_4_FRESH_DEMOS_STARTED = 1
PHASE13_2_ATTEMPT_4_DEMOS_EXECUTED = 0
OLD_EVIDENCE_REUSED_AS_ATTEMPT4_PASS = 0
UPLOAD_PROCESS_MEMORY_DEPENDENCY = 0
MANUAL_NORMALIZED_EXPORT_PRELOAD = 0
RUNTIME_REPARSE_FALLBACK = 0
ALL_HANDCRAFTED_INJECTION_COUNTERS = 0
P13X2_ACCEPTANCE = 0/8
P13_R4_001 = OPEN_REVIEWER_ACTION_REQUIRED
P13_R4_002 = OPEN_REVIEWER_ACTION_REQUIRED
RELEASE_CRITICAL_INTEGRATION_DEFECTS = 2
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
UNCLASSIFIED_RELEASE_GAPS = 0
PROVIDER_EXTERNAL_EVENTS = 0
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
CURRENT_SCOPE_BASELINE_HASH = eb91799bf1c8e19311077c6058e91da29bb01907583f0403855202473c4e5e94
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
FACT_MODEL_HASH_IMPACT_BY_ATTEMPT_4 = NO
SCOPE_BASELINE_HASH_IMPACT_BY_ATTEMPT_4 = NO
BASELINE_DETERMINISM = PASS
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
REAL_LLM_CALLS = 0
PHASE_13_3 = BLOCKED_BY_PHASE13_2_ATTEMPT_4
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
FAILED_RETAINED_TASK_BLOCKS = 4
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 4
PHASE14_CREATED = NO
```

# Phase 13-1 Integration Fix-Forward #4 Result

Status: PASS

Completion time: 2026-08-12 21:00:02 +08:00

`P13-R4-001` selected Branch B. The historical Demo 1 prompt expressed
composition distribution, while the sealed demo required explicit composition
space. The current prompt authority was corrected; production Intent,
Eligibility and Planner behavior did not change. Demo 1 now selects exactly
`dataset.materials_explorer` and `dataset.composition_space`, and all seven
canonical prompts pass semantic coverage (`7/7`) without invented dependencies,
forced Plan upgrades or unrequested capabilities.

`P13-R4-002` was caused by the Workspace projection omitting the Report panel
before a Report existed and the frontend treating scientific
`LEGACY_READ_ONLY` as a global Report Finalize prohibition. Report actions now
derive independently from exact current Profile, Intent, Eligibility, Plan,
terminal Job, scope and integrity facts. Current valid Plan 0.1 Finalize passes;
legacy incomplete and stale Plan 0.1 sources remain unavailable with typed
reasons; cross-project sources remain rejected; Plan 0.2 is unchanged.

The fresh Demo 1 smoke used real PostgreSQL, Redis, MinIO and a fresh Worker.
Plan `plan_7d0d916dd60945fcb28a9879` executed two registered tools and persisted
eight Artifacts. Chromium finalized Report
`report_884dec9549b6617dc4b10d562542a61a` with paired non-executable Recipe
`recipe_884dec9549b6617dc4b10d562542a61a`. Recipe inspection caused zero Plan,
Job, queue, ToolCall or Artifact growth.

Backend: `1406 passed, 52 skipped`; required services separately passed with
zero required skips. Frontend: `458 passed`; Phase 13 focused/governance:
`89 passed`. Typecheck, build, lock, diff, PostgreSQL, Redis, MinIO,
Chromium/Firefox/WebKit/390x844, Linux/Windows, security, secret scan and
manifest all PASS. Failed candidate
`f3ec578acd1cfaddb9437d74869cf437ad17c848` / CI `31594862635` is retained.
Corrected implementation `71985085ac0ab0dbe36b141b88c0251d76892689`
passed exact-SHA CI `31597787296`.

```text
PHASE_13_1_FIX_FORWARD_4 = PASS
P13_R4_001 = CLOSED
P13_R4_002 = CLOSED
CANONICAL_DEMO_SEMANTIC_COVERAGE = 7/7
DEMO1_REQUIRED_CAPABILITY_COVERAGE = COMPLETE
FRESH_DEMO1_PRODUCT_CLOSURE_SMOKE = PASS
CURRENT_VALID_PLAN01_REPORT_FINALIZE = PASS
LEGACY_INCOMPLETE_PLAN01_REPORT_FINALIZE = UNAVAILABLE_WITH_TYPED_REASON
STALE_PLAN01_REPORT_FINALIZE = UNAVAILABLE_WITH_TYPED_REASON
PLAN02_REPORT_BEHAVIOR = UNCHANGED
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
D0_REAL_UPLOAD_TO_FRESH_WORKER = PASS
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
FACT_MODEL_HASH_IMPACT = NO
CURRENT_SCOPE_BASELINE_HASH = f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455
SCOPE_BASELINE_HASH_IMPACT = YES
BASELINE_DETERMINISM = PASS
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_ANALYSISINTENT_VERSION = 0
NEW_ELIGIBILITY_VERSION = 0
NEW_ANALYSISPLAN_VERSION = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
PHASE13_2_ATTEMPT_1 = FAILED_HISTORICAL
PHASE13_2_ATTEMPT_2 = FAILED_RERUN_HISTORICAL
PHASE13_2_ATTEMPT_3 = FAILED_RERUN_HISTORICAL
PHASE13_2_ATTEMPT_4 = FAILED_RERUN_HISTORICAL
PHASE13_2_ATTEMPT_5 = REVIEWER_GATE / NOT_EXECUTED / NOT_QUEUED
P13X2_ACCEPTANCE = 0/8
FIX_FORWARD_4_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
FIX_FORWARD_4_COMPLETION_RECORDED
FIX_FORWARD_4_QUEUE_ARCHIVED
FAILED_RETAINED_TASK_BLOCKS = 4
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 4
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Release Scope Exception #1 Failure-Evidence CI Record

The initial failure-evidence candidate
`f3871ab44287b658e64fc1c82b90472d890ebdba` retained CI `31619480956` as a
failed candidate: one current semantic-coverage test did not recognize explicit
typed phonon fixture modes. The test-only corrected candidate
`0429b88be6fac1c1d602edfe9fdeaf3f3555e9e1` passed exact-SHA CI
`31620258786`, including Python unit/governance, PostgreSQL/Redis/MinIO service
integration, frontend typecheck/build and retained browser evidence, plus
Linux/Windows scientific replay.

This is failure-evidence verification only. `P13-RSE1-001` remains open,
Release Scope Exception #1 remains failed, completion/archive are not
applicable, all seven queue blocks remain retained, and Attempt 6 remains
unqueued.

```text
RELEASE_SCOPE_EXCEPTION_1_FAILURE_EVIDENCE_SHA = 0429b88be6fac1c1d602edfe9fdeaf3f3555e9e1
RELEASE_SCOPE_EXCEPTION_1_FAILURE_EVIDENCE_EXACT_SHA_CI = 31620258786 / PASS
RELEASE_SCOPE_EXCEPTION_1_COMPLETION_RECORDED = NOT_APPLICABLE
RELEASE_SCOPE_EXCEPTION_1_QUEUE_ARCHIVED = NO
```

# Phase 13-2 Attempt 5
# Seven Canonical Real-User E2E Demonstrations Result

Status: FAILED / REVIEWER_ACTION_REQUIRED

Completion time: 2026-08-12 22:09:13 +08:00

Attempt 5 passed its repository-authority, semantic-coverage, Level C, Level
C2, D0, durable-source, and Demo 1 product-closure entry gates. The execution
then started five entirely fresh canonical demos. Demos 1-3 completed through
real PostgreSQL Jobs, Redis, fresh Workers, registered Adapters, persisted
Artifacts, Workspaces, Chromium Report Finalize, and paired non-executable
Recipes. No historical execution was used as current PASS evidence.

The P0 stop rule was activated by two release-critical product integration
defects. `P13-R5-001` affects Demo 4: a fresh Plan 0.2 trajectory Job completed
RDF, MSD, and diffusion and persisted twelve Artifacts, but its projected
Workspace was rejected for Report actions as `WORKSPACE_SOURCE_NOT_CURRENT`.
`P13-R5-002` affects Demo 5: the real phonon upload persisted a Profile with
only structure resource semantics, so natural-language Intent validation
returned `INTENT_PROFILE_CAPABILITY_MISSING` before Plan or Job creation.
Production and scientific code were not changed. Demos 6-7 and all downstream
negative/provider/cross-browser aggregate work were not executed after the P0
stop.

Evidence commit `d8d1966ff0fb419ff8299ec440c1af8e0c349f24` passed exact-SHA
CI `31603622900`. CI recorded `1410 passed, 1 skipped, 51 deselected` for the
main Python suite, `50 passed, 0 skipped` for service-backed PostgreSQL/Redis/
MinIO integration, and PASS for frontend typecheck/build and retained browser
replays plus Linux/Windows scientific replay. Attempt 5 evidence checks passed
`4/4`; lock, diff, security, secret scan, and the 132-entry evidence manifest
passed. Completion and queue archive are not applicable to this failed attempt.

```text
PHASE_13_2_ATTEMPT_5 = FAILED / REVIEWER_ACTION_REQUIRED
PHASE13_2_ATTEMPT_1 = FAILED_HISTORICAL
PHASE13_1_FIX_FORWARD_1 = PASS
PHASE13_2_ATTEMPT_2 = FAILED_RERUN_HISTORICAL
PHASE13_1_FIX_FORWARD_2 = PASS
PHASE13_2_ATTEMPT_3 = FAILED_RERUN_HISTORICAL
PHASE13_1_FIX_FORWARD_3 = PASS
PHASE13_2_ATTEMPT_4 = FAILED_RERUN_HISTORICAL
PHASE13_1_FIX_FORWARD_4 = PASS

SEMANTIC_COVERAGE = 7/7 PASS
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
D0_REAL_UPLOAD_TO_FRESH_WORKER = PASS
DEMO1_PRODUCT_CLOSURE_REGRESSION = PASS

DEMO_1_STATUS = PASS
DEMO_2_STATUS = PASS
DEMO_3_STATUS = PASS
DEMO_4_STATUS = FAIL_PRODUCT_INTEGRATION
DEMO_5_STATUS = FAIL_PRODUCT_INTEGRATION
DEMO_6_STATUS = NOT_EXECUTED_AFTER_P0_STOP
DEMO_7_STATUS = NOT_EXECUTED_AFTER_P0_STOP
ATTEMPT_5_FRESH_DEMOS_STARTED = 5
ATTEMPT_5_FULL_DEMOS_EXECUTED = 3
DEMO_PASS_OR_EXPLICIT_LIMIT = 3/7
OLD_EVIDENCE_REUSED_AS_ATTEMPT5_PASS = 0

P13_R5_001 = OPEN_REVIEWER_ACTION_REQUIRED
P13_R5_001_CLASS = FRESH_TRAJECTORY_WORKSPACE_REPORT_SOURCE_CURRENTNESS_DEFECT
P13_R5_002 = OPEN_REVIEWER_ACTION_REQUIRED
P13_R5_002_CLASS = REAL_UPLOAD_PHONON_PROFILE_CAPABILITY_HANDOFF_DEFECT
RELEASE_CRITICAL_INTEGRATION_DEFECTS = 2
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
PROVIDER_EXTERNAL_EVENTS = 0
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0

UPLOAD_PROCESS_MEMORY_DEPENDENCY = 0
MANUAL_NORMALIZED_EXPORT_PRELOAD = 0
RUNTIME_REPARSE_FALLBACK = 0
ALL_HANDCRAFTED_INJECTION_COUNTERS = 0
P13X2_ACCEPTANCE = 0/8

CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
CURRENT_SCOPE_BASELINE_HASH = f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
FACT_MODEL_HASH_IMPACT_BY_ATTEMPT_5 = NO
SCOPE_BASELINE_HASH_IMPACT_BY_ATTEMPT_5 = NO
BASELINE_DETERMINISM = PASS

REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain

ATTEMPT_5_EVIDENCE_VERIFIED_BY_EXACT_SHA_CI
ATTEMPT_5_COMPLETION_RECORDED = NOT_APPLICABLE
PHASE13_2_QUEUE_ARCHIVED = NO

FAILED_RETAINED_TASK_BLOCKS = 5
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 5
PHASE_13_3 = BLOCKED_BY_PHASE13_2_ATTEMPT_5
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 13-1 Integration Fix-Forward #5 Result

Status: BLOCKED / DEMO5_INITIAL_RELEASE_ENTRY_AUTHORITY_CONFLICT

Time: 2026-08-12 23:25:00 +08:00

`P13-R5-001` was reproduced from the retained real Attempt 5 PostgreSQL state.
Intent and Eligibility used top-level `DataProfile.version = 2` because the
Trajectory Profile legitimately had `sampleIdentity = null`; Workspace
projection omitted that fallback and persisted `datasetVersion = null`.
The bounded implementation now applies the same fallback and verifies the
immutable Workspace source snapshot against the exact execution source. The
Workspace/Report focused suite passed `29/29`. Because the Branch C hard stop
occurred before the required fresh Demo 4 service/browser smoke, the full
R5-001 closure gate is not claimed.

The required R5-002 authority audit selected Branch C. Attempt 5's exact user
action was public `/datasets/upload` with `stable_band.json`, `total_dos.json`
and `POSCAR`. Phase 11 classifies generic phonon YAML/JSON as `MAPPING_ONLY` and
the product has no supported user-visible typed phonon import/selection path.
Exact schemas, internal normalized mappers, C/C2 preparation, runtime resolver,
Adapters and viewers exist, but none constitutes legal normal-user ingestion.
No parser, support matrix row, hidden endpoint, Profile injection or input
support promotion was added.

```text
PHASE_13_1_FIX_FORWARD_5 = BLOCKED / DEMO5_INITIAL_RELEASE_ENTRY_AUTHORITY_CONFLICT
P13_R5_001 = IMPLEMENTATION_CORRECTED / FRESH_DEMO4_SMOKE_NOT_EXECUTED
P13_R5_001_MISMATCH_FIELD = datasetVersion
P13_R5_002 = OPEN_REVIEWER_AUTHORITY_REQUIRED
P13_R5_002_HISTORICAL_CLASS = REAL_UPLOAD_PHONON_PROFILE_CAPABILITY_HANDOFF_DEFECT
P13_R5_002_SELECTED_BRANCH = C
P13_R5_002_FINAL_CLASS = DEMO5_INITIAL_RELEASE_ENTRY_AUTHORITY_CONFLICT
PHONON_DIRECT_UPLOAD_SUPPORT_PROMOTION = 0
INPUT_SUPPORT_PROMOTIONS = 0
PHASE11_INPUT_SUPPORT_MATRIX_CHANGED = NO
CANONICAL_DEMO_SEMANTIC_COVERAGE = 7/7 PASS
CANONICAL_USER_INGESTION_FIDELITY = 6/7 BLOCKED
USER_ENTRY_CONTRACT_MISMATCHES = 1
INTERNAL_ONLY_ENTRY_PATHS_USED_AS_USER_PASS = 0
FRESH_DEMO4_PRODUCT_CLOSURE_SMOKE = NOT_EXECUTED_AFTER_BRANCH_C_STOP
FRESH_DEMO5_PRODUCT_CLOSURE_SMOKE = NOT_APPLICABLE_BRANCH_C
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
D0_REAL_UPLOAD_TO_FRESH_WORKER = PASS
DEMO1_PRODUCT_CLOSURE_REGRESSION = PASS
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
CURRENT_SCOPE_BASELINE_HASH = f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455
FACT_MODEL_HASH_IMPACT = NO
SCOPE_BASELINE_HASH_IMPACT = NO
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
PHASE13_2_ATTEMPT_6 = BLOCKED / NOT_AUTHORIZED
PHASE13_2_ATTEMPT_6_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
FAILED_RETAINED_TASK_BLOCKS = 6
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 6
FIX_FORWARD_5_IMPLEMENTATION_EXACT_SHA_CI = NOT_RUN_BRANCH_C_STOP
FIX_FORWARD_5_COMPLETION_RECORDED = NO
FIX_FORWARD_5_QUEUE_ARCHIVED = NO
```

# Phase 13-1 Release Scope Exception #1 Result

Status: FAILED / REVIEWER_ACTION_REQUIRED

Time: 2026-08-13 00:20:00 +08:00

The authorized bounded typed `PhononBand`/`PhononDos` import candidate reused
the existing `/datasets/upload`, strict Phase 10H resource contracts,
PostgreSQL Dataset/DataProfile metadata, and MinIO normalized source authority.
Generic phonon JSON remained mapping-only. Focused backend tests passed 10/10,
PlannerWorkbench passed 33/33, retained phonon contract/Adapter tests passed
76/76, and frontend typecheck passed.

Fresh Demo 4 reached a completed three-ToolCall Job, twelve persisted Artifacts,
a current Workspace, and eligible Report actions. Before its Chromium finalize,
fresh Demo 5 exposed a new P0 and activated the stop rule. Demo 5 passed typed
Band/DOS import, Profile, Intent, Eligibility, PlanValidator, PostgreSQL Job,
Redis enqueue, a fresh Worker, four registered ToolCalls, and 27 persisted
Artifacts. Workspace creation then returned `PANEL_CAP_EXCEEDED`: deterministic
projection exceeds the fixed 32-panel contract. This is `P13-RSE1-001`, class
`CANONICAL_PHONON_JOB_EXCEEDS_WORKSPACE_PANEL_CAP`.

No repair for the new finding was attempted. Demo 4/5 UI Finalize, full
regression, new Fact/Scope hashes, exact-SHA CI, completion, and queue archive
are not applicable to this failed candidate. R5-001 and R5-002 remain open.

Failed candidate `f3871ab44287b658e64fc1c82b90472d890ebdba` ran CI
`31619480956`. Its Python job reported `1423 passed` and one governance failure:
the current seven-demo coverage helper recognized only historical
`normalized_mapping`, not the new explicit typed import fixture modes. The
subsequent candidate changes only that test/evidence dispatch and does not
alter product behavior or the `P13-RSE1-001` conclusion.

```text
PHASE_13_1_RELEASE_SCOPE_EXCEPTION_1 = FAILED / REVIEWER_ACTION_REQUIRED
P13_RSE1_001 = OPEN_REVIEWER_ACTION_REQUIRED
P13_RSE1_001_SEVERITY = P0
P13_RSE1_001_CLASS = CANONICAL_PHONON_JOB_EXCEEDS_WORKSPACE_PANEL_CAP
P13_R5_001 = IMPLEMENTATION_CORRECTED / FRESH_DEMO4_SMOKE_NOT_COMPLETED
P13_R5_002 = OPEN_REVIEWER_ACTION_REQUIRED
TYPED_PHONON_BAND_CANDIDATE = REACHED_FRESH_WORKER
TYPED_PHONON_DOS_CANDIDATE = REACHED_FRESH_WORKER
GENERIC_PHONON_YAML_JSON = MAPPING_ONLY
GENERIC_PHONON_JSON_AUTO_PROMOTION = 0
FRESH_DEMO4_PRODUCT_CLOSURE_SMOKE = NOT_COMPLETED_AFTER_P0_STOP
FRESH_DEMO5_PRODUCT_CLOSURE_SMOKE = FAIL_PRODUCT_INTEGRATION
DEMO5_TOOLCALLS = 4
DEMO5_PERSISTED_ARTIFACTS = 27
DEMO5_WORKSPACES = 0
RELEASE_CRITICAL_INTEGRATION_GAPS = 1
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
CURRENT_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
CURRENT_SCOPE_BASELINE_HASH = f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
FACT_MODEL_HASH_IMPACT = NOT_APPLIED_AFTER_P0_STOP
SCOPE_BASELINE_HASH_IMPACT = NOT_APPLIED_AFTER_P0_STOP
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
PHASE13_2_ATTEMPT_6 = REVIEWER_GATE / NOT_EXECUTED / NOT_QUEUED
P13X2_ACCEPTANCE = 0/8
FAILED_RETAINED_TASK_BLOCKS = 7
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 7
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 13-1 Integration Fix-Forward #6 Result

Status: PASS

Time: 2026-08-13 12:58:00 +08:00

Implementation `0867a69a587bf8e0ddb5aaeec7a177808a69e6f1` passed exact-SHA
CI `31667748439`. This candidate includes the bounded R5-001 correction, the
authorized typed phonon import candidate, generic logical-surface Workspace
projection, evidence, tests, and generated Fact/Scope authorities.

`P13-RSE1-001` is closed as a Workspace panel projection cardinality defect.
The historical Demo 5 projection had six structural plus 27 Artifact-derived
candidate panels. The corrected projection has six structural panels and one
exact Job-bound Results/Artifact Gallery surface. All 27 Artifacts remain
checksum-, ToolCall-, and lineage-bound and exactly reachable. The cap remains
32; exact-32 passes and 33 distinct non-groupable surfaces still return
`PANEL_CAP_EXCEEDED`, with no truncation or historical reprojection.

Fresh Demo 4 completed through three ToolCalls, 12 persisted Artifacts,
Workspace `workspace_7b853905207a11183b981c3cea68fc05`, Chromium UI
Finalize, Report `report_68f398a22f6ece8286d3c65d57ef48fa`, and Recipe
`recipe_68f398a22f6ece8286d3c65d57ef48fa`. Exact execution, Workspace,
and Report source snapshots agree; stale, hash, and cross-project negatives
remain rejected. `P13-R5-001` is closed.

Fresh Demo 5 completed from explicit typed PhononBand and PhononDos import
through DataProfile 2.4, Intent 1.0, Eligibility 1.0, Planner, PlanValidator,
PostgreSQL Job `job_66e90ccd3a9648ceb39d576a`, Redis, fresh Worker, four
registered ToolCalls, 27 Artifacts, Workspace
`workspace_bea76bb13adc0987324ad23cb1fa6413`, seven panels, exact Gallery
reachability, Chromium UI Finalize, Report
`report_044097cefce37d3471a7846b63c7604b`, and Recipe
`recipe_044097cefce37d3471a7846b63c7604b`. Unknown input refs and Recipe
execution growth are zero. `P13-R5-002` is closed.

The failed Release Scope Exception #1 remains immutable historical evidence.
Its authorized scope is sealed by Fix-Forward #6: typed PhononBand/PhononDos
imports are `SUPPORTED_WITH_LIMITS`, while generic phonon YAML/JSON remains
`MAPPING_ONLY`; no other support or scientific capability is promoted.

Validation: backend `1432 passed, 50 skipped`; frontend `460 passed` in 71
files; Phase 13 focused/governance `113 passed`; service suite `7 passed` with
zero required skips; Chromium, Firefox, WebKit, and 390x844 checks `4/4 PASS`;
typecheck, build, lock, diff, Linux, Windows, security, secret scan, and manifest
PASS. npm audit is `UNAVAILABLE_CONFIGURED_MIRROR_NOT_IMPLEMENTED`.

```text
PHASE_13_1_INTEGRATION_FIX_FORWARD_6 = PASS
P13_RSE1_001 = CLOSED
P13_RSE1_001_HISTORICAL_CLASS = CANONICAL_PHONON_JOB_EXCEEDS_WORKSPACE_PANEL_CAP
P13_RSE1_001_FINAL_CLASS = WORKSPACE_PANEL_PROJECTION_CARDINALITY_DEFECT
MAX_PANELS_PER_WORKSPACE = 32
PANEL_CAP_CHANGE = NO
ARTIFACT_COUNT_TO_PANEL_COUNT_ONE_TO_ONE = NO
PANEL_TRUNCATION = 0
DROPPED_ARTIFACTS = 0
UNREACHABLE_ARTIFACTS = 0
PANEL_CAP_32_CASE = PASS
PANEL_CAP_33_CASE = PANEL_CAP_EXCEEDED
P13_R5_001 = CLOSED
FRESH_DEMO4_PRODUCT_CLOSURE_SMOKE = PASS
FRESH_TRAJECTORY_WORKSPACE_SOURCE_CURRENTNESS = PASS
TRAJECTORY_STALE_SOURCE_REJECTION = PASS
P13_R5_002 = CLOSED
TYPED_PHONON_BAND_USER_IMPORT = SUPPORTED_WITH_LIMITS / PASS
TYPED_PHONON_DOS_USER_IMPORT = SUPPORTED_WITH_LIMITS / PASS
GENERIC_PHONON_YAML_JSON = MAPPING_ONLY
GENERIC_PHONON_JSON_AUTO_PROMOTION = 0
FRESH_DEMO5_PRODUCT_CLOSURE_SMOKE = PASS
FRESH_DEMO5_WORKSPACE_PROJECTION = PASS
FRESH_DEMO5_PANEL_CAP_EXCEEDED = 0
FRESH_DEMO5_ARTIFACT_REACHABILITY = COMPLETE
RELEASE_SCOPE_EXCEPTION_1_AUTHORIZED_SCOPE = SEALED_BY_FIX_FORWARD_6
FIX_FORWARD_5_BLOCK = RESOLVED_BY_FIX_FORWARD_6
CANONICAL_DEMO_SEMANTIC_COVERAGE = 7/7
CANONICAL_USER_INGESTION_FIDELITY = 7/7
USER_ENTRY_CONTRACT_MISMATCHES = 0
INTERNAL_ONLY_ENTRY_PATHS_USED_AS_USER_PASS = 0
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
D0_REAL_UPLOAD_TO_FRESH_WORKER = PASS
DEMO1_PRODUCT_CLOSURE_REGRESSION = PASS
RELEASE_CRITICAL_INTEGRATION_GAPS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
INPUT_SUPPORT_MATRIX_CHANGED = YES
AUTHORIZED_TYPED_IMPORT_SUPPORT_ADDITIONS = 2
OTHER_INPUT_SUPPORT_PROMOTIONS = 0
SCIENTIFIC_CAPABILITY_PROMOTIONS = 0
OLD_FACT_MODEL_HASH = e0248d502e4a442bb9596a8d2f6fe6d7fdefe61c41121ae08736734ce4004a06
FACT_MODEL_HASH_IMPACT = YES
CURRENT_FACT_MODEL_HASH = 92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a
OLD_SCOPE_BASELINE_HASH = f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455
SCOPE_BASELINE_HASH_IMPACT = YES
CURRENT_SCOPE_BASELINE_HASH = bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
BASELINE_DETERMINISM = PASS
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_SCIENTIFIC_ADAPTERS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
FIX_FORWARD_6_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
FIX_FORWARD_6_COMPLETION_RECORDED
FIX_FORWARD_5_BLOCK_RESOLVED_BY_FIX_FORWARD_6
RELEASE_SCOPE_EXCEPTION_1_FAILURE_RESOLVED_BY_FIX_FORWARD_6
PHASE13_2_ATTEMPT_6 = REVIEWER_GATE / NOT_EXECUTED / NOT_QUEUED
PHASE13_2_ATTEMPT_6_DEMOS_EXECUTED = 0
P13X2_ACCEPTANCE = 0/8
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## 2026-08-16 Phase D Live Qualification Environment Seal

Status: BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED

Entry repository SHA is
`08939f1b72ce37f153a0bdc18eee213f336b3636`, matching `origin/master`.
The required frozen qualification ZIP is absent from its authority path under
`_qualification/inputs/`. A same-named untracked ZIP exists at repository root,
has 19,073,044 bytes, and matches the expected SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`,
but Phase D did not copy, move, repackage, or accept it as a path substitute.

Blocker `PHASE_D-B001 = QUALIFICATION_PACKAGE_MISSING_AT_AUTHORITY_PATH` stopped
the run before extraction, internal manifest verification, service startup,
worker startup, browser smoke, or provider credential inspection. Formal case,
LLM, Job, and Artifact counters remain zero. Production code, qualification
package, and scientific fixture changes remain zero. Local blocked evidence is
retained under `_qualification/evidence/phase_d/`; no Phase E task was created.

```text
PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED
READY_FOR_PHASE_E = NO
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
BLOCKERS = [PHASE_D-B001]
```

# Phase 13-5 Final Regression + Release Acceptance Local Validation

Status: `LOCAL_VALIDATION_PASS_PENDING_EXACT_SHA_CI`.

Seven fresh isolated, service-backed canonical paths passed without reusing
Attempt6 runtime entities: 18 registered ToolCalls, 85 persisted Artifacts,
seven Job-derived Workspaces, seven UI-finalized Reports, and seven paired
non-executable Recipes. Demo5 used explicit typed PhononBand and PhononDos
imports; generic phonon YAML/JSON remained mapping-only. Artifact reachability,
32/33 panel-cap protection, frozen authority hashes, documentation/reproducibility,
browser, security, and retained regression gates passed locally. No production,
scientific, support, or dependency change was made. Exact-SHA CI, completion,
and queue archive remain pending.

# Phase 13-4 Targeted Final Product Polish Result

Status: `PASS / TARGETED_FINAL_PRODUCT_POLISH_COMPLETE`

Completion time: `2026-08-13 23:42:03 +08:00`

Implementation/evidence SHA:
`40403cfa19451cc9a473c41bddecfe053e1a5fea`

Exact-SHA CI: `31715231470` `PASS`

The Phase13-3 handoff produced two presentation candidates. `P13-POLISH-001`
is `ALREADY_RESOLVED` because the current-facing UTF-8 scan found zero mojibake
hits. `P13-POLISH-002` is the sole implemented item: the existing Planner
top-bar Help control is now a localized, keyboard-accessible link to current
Initial Release documentation. It changes no product execution, API, backend,
scientific, Planner, Runtime, Workspace, Report, Recipe, capability, input
support, canonical prompt, fixture, Fact, Scope, or reproducibility authority.

Candidate `34f7cb7cea3db351edff0d3b39ff7fe39cd7e192` failed CI
`31713598663` only because GitHub shallow checkout lacked sealed entry object
`d415d05...` for evidence nonchange checks. Candidate
`40403cfa19451cc9a473c41bddecfe053e1a5fea` corrects that CI-only portability
issue and passed all exact-SHA jobs.

```text
PHASE_13_4 = PASS / TARGETED_FINAL_PRODUCT_POLISH_COMPLETE
HANDOFF_POLISH_ITEMS_DISCOVERED = 2
ACTIONABLE_POLISH_ITEMS = 1
POLISH_ITEMS_IMPLEMENTED = 1
POLISH_ITEMS_SKIPPED_WITH_REASON = 1
UNAUTHORIZED_POLISH_ITEMS = 0

CURRENT_FACT_MODEL_HASH = 92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a
FACT_MODEL_HASH_IMPACT_BY_PHASE13_4 = NO
CURRENT_SCOPE_BASELINE_HASH = bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba
SCOPE_BASELINE_HASH_IMPACT_BY_PHASE13_4 = NO
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4
REPRO_MANIFEST_HASH = 931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2

BACKEND = 1450 passed / 1 skipped / 51 integration deselected
FRONTEND = 460 passed
PHASE13_FOCUSED = 133 passed
POSTGRESQL_REDIS_MINIO = PASS / 0 skipped
CHROMIUM = PASS
FIREFOX = PASS
WEBKIT = PASS
MOBILE_390X844 = PASS
LINUX_REPLAY = PASS
WINDOWS_REPLAY = PASS
TYPECHECK = PASS
BUILD = PASS
UV_LOCK_CHECK = PASS
GIT_DIFF_CHECK = PASS
SECURITY = PASS
SECRET_SCAN = PASS
MANIFEST_SELF_CHECK = PASS
npm audit = UNAVAILABLE_CONFIGURED_MIRROR_NOT_IMPLEMENTED

BACKEND_PRODUCTION_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0

PHASE13_4_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_4_COMPLETION_RECORDED
PHASE_13_5 = REVIEWER_GATE / AWAITING_REVIEWER_PROMPT
PHASE13_5_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-4 Queue Archive

The implementation/evidence SHA `40403cfa19451cc9a473c41bddecfe053e1a5fea`
passed exact-SHA CI `31715231470`; completion commit `46c70c2ed49b30e44ab33450540d1b90aacdea2c`
was pushed before removing the completed Phase 13-4 task block. The completed
result and failed candidate remain permanently recorded above and in the Phase
13-4 evidence tree.

```text
PHASE13_4_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_4_COMPLETION_RECORDED
PHASE13_4_QUEUE_ARCHIVED
TASK_BLOCK_COUNT = 0
EXECUTABLE_PENDING_TASKS = 0
PHASE_13_5 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_5_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-5 Queue Archive

After verification of completion commit `1afed7f982bdd6d2b5e9bef50e2cf4b14b984d32`,
the completed Phase 13-5 task block was removed. The validation result and all
evidence remain permanently retained.

```text
PHASE13_5_QUEUE_ARCHIVED
TASK_BLOCK_COUNT = 0
EXECUTABLE_PENDING_TASKS = 0
PHASE_13_6 = REVIEWER_GATE / AWAITING_REVIEWER_PROMPT
PHASE13_6_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Fix-Forward #6 Queue Archive

The completed Fix-Forward #6 block, resolved Fix-Forward #5 blocked block, and
historical failed Release Scope Exception #1 queue block are archived after
their permanent `results.md` and evidence provenance was verified. The five
failed Phase 13-2 Attempt blocks remain. Attempt 6 is not executed or queued.

```text
FIX_FORWARD_6_QUEUE_ARCHIVED
FIX_FORWARD_5_BLOCK_RESOLVED_BY_FIX_FORWARD_6
RELEASE_SCOPE_EXCEPTION_1_FAILURE_RESOLVED_BY_FIX_FORWARD_6
FAILED_RETAINED_PHASE13_2_ATTEMPTS = 5
BLOCKED_FIX_FORWARD_TASKS = 0
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 5
PHASE13_2_ATTEMPT_6 = REVIEWER_GATE / NOT_EXECUTED / NOT_QUEUED
PHASE13_2_ATTEMPT_6_EXECUTABLE_TASK_CREATED = NO
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 13-2 Attempt 6 Result

Status: `PASS`

Completion time: `2026-08-13 17:10:00 +08:00`

Implementation/evidence SHA:
`5ddf2c0508a1f61642808a35774917fa3b54b0b0`

Exact-SHA CI: `31682863560` `PASS`

Seven fresh canonical real-user product paths completed from current user entry
through PostgreSQL/MinIO durable identity, DataProfile 2.4, natural-language
Intent 1.0, Eligibility 1.0, capability-aware Planner, validated Plan 0.1/0.2,
PostgreSQL Job, Redis, fresh QueueWorkerRuntime, registered Adapters, persisted
Artifacts, Job-derived Workspace, typed Viewer/Gallery, Chromium Report Preview
and UI Finalize, persisted Report, and paired non-executable Recipe.

```text
PHASE_13_2_ATTEMPT_6 = PASS
ATTEMPT6_FRESH_DEMOS_STARTED = 7
ATTEMPT6_FULL_DEMOS_EXECUTED = 7
DEMO_PASS_OR_EXPLICIT_LIMIT = 7/7
OLD_EVIDENCE_REUSED_AS_ATTEMPT6_PASS = 0

DEMO_1_STATUS = PASS
DEMO_2_STATUS = PASS
DEMO_3_STATUS = PASS
DEMO_4_STATUS = PASS
DEMO_5_STATUS = PASS
DEMO_6_STATUS = PASS
DEMO_7_STATUS = PASS

TOOLCALLS = 18
PERSISTED_ARTIFACTS = 85
WORKSPACE_PANELS_PER_DEMO = 7
UNREACHABLE_ARTIFACTS = 0
PANEL_CAP_32_CASE = PASS
PANEL_CAP_33_CASE = PANEL_CAP_EXCEEDED
PANEL_TRUNCATION = 0

TYPED_PHONON_BAND_IMPORT = SUPPORTED_WITH_LIMITS
TYPED_PHONON_DOS_IMPORT = SUPPORTED_WITH_LIMITS
GENERIC_PHONON_YAML_JSON = MAPPING_ONLY

CANONICAL_DEMO_SEMANTIC_COVERAGE = 7/7
CANONICAL_USER_INGESTION_FIDELITY = 7/7
LEVEL_C = 7/7 PASS
LEVEL_C2 = 7/7 PASS
D0_REAL_UPLOAD_TO_FRESH_WORKER = PASS
P13X2_ACCEPTANCE = 8/8

BACKEND = 1438 passed
FRONTEND = 460 passed
PHASE13_FOCUSED = 121 passed
REQUIRED_SERVICE_TESTS = 8 passed / 0 skipped
CHROMIUM = PASS
FIREFOX = PASS
WEBKIT = PASS
MOBILE_390X844 = PASS
LINUX_REPLAY = PASS
WINDOWS_REPLAY = PASS
TYPECHECK = PASS
BUILD = PASS
UV_LOCK_CHECK = PASS
GIT_DIFF_CHECK = PASS
SECURITY = PASS
SECRET_SCAN = PASS
MANIFEST_SELF_CHECK = PASS

CURRENT_FACT_MODEL_HASH = 92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a
CURRENT_SCOPE_BASELINE_HASH = bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba
FACT_MODEL_HASH_IMPACT_BY_ATTEMPT6 = NO
SCOPE_BASELINE_HASH_IMPACT_BY_ATTEMPT6 = NO

REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
MAX_PANELS_PER_WORKSPACE = 32

PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_SCIENTIFIC_ADAPTERS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
NEW_LLM_CALL_SITES = 0

ATTEMPT_6_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
ATTEMPT_6_COMPLETION_RECORDED
PHASE_13_3 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-2 Queue Archive

Attempt6 PASS, implementation exact-SHA CI `31682863560`, and completion commit
`dd4ac01` were verified before archive. Attempt1-5 historical failures and the
Attempt6 PASS remain permanently recorded in `results.md` and evidence. All six
Phase13-2 TASK blocks are removed; no Phase13-3 task is created.

```text
PHASE13_2_QUEUE_ARCHIVED
ATTEMPT_6_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
ATTEMPT_6_COMPLETION_RECORDED
FAILED_RETAINED_TASK_BLOCKS = 0
EXECUTABLE_PENDING_TASKS = 0
TASK_BLOCK_COUNT = 0
PHASE_13_3 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_3_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

# Phase 13-3 Documentation + Reproducibility Package Result

Status: `PASS / DOCUMENTATION_AND_REPRODUCIBILITY_PACKAGE_COMPLETE`

Completion time: `2026-08-13 21:29:27 +08:00`

Implementation/evidence SHA:
`c3aabd055e067c5a52a0c0238c625dbc035a96f0`

Exact-SHA CI: `31703805747` `PASS`

Phase 13-2 Attempt 6 authority, P13X2 `8/8`, current Fact/Scope/Phase12
authorities, current input support, scientific limitations, provider policy,
security boundaries, seven canonical prompts, and eleven canonical fixtures
are reconciled into current human and machine-readable release documentation.

The deterministic reproducibility manifest semantic hash is
`931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2`.
Text fixture evidence uses canonical UTF8/LF hashing; binary evidence uses raw
bytes. Windows clean-checkout regeneration matches the committed package, and
CI verifies Linux/Windows manifest parity.

```text
PHASE_13_3 = PASS / DOCUMENTATION_AND_REPRODUCIBILITY_PACKAGE_COMPLETE

ATTEMPT6_AUTHORITY_RECONCILED = PASS
P13X2_ACCEPTANCE = 8/8

CANONICAL_DEMO_DOCUMENTATION = 7/7
CANONICAL_DEMO_REPRO_CONTRACTS = 7/7
CANONICAL_DEMO_FIXTURE_HASHES = 7/7
CANONICAL_DEMO_PROMPTS = 7/7
CANONICAL_DEMO_USER_ENTRY_CONTRACTS = 7/7

CANONICAL_FIXTURE_RECORDS = 11
REPRO_MANIFEST_HASH = 931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2
REPRO_MANIFEST_DETERMINISM = PASS
LINUX_WINDOWS_REPRO_MANIFEST_PARITY = PASS
CLEAN_CHECKOUT_REPRO_BOOTSTRAP = PASS

POSTGRESQL_REPRO_INSTRUCTIONS = PASS
REDIS_REPRO_INSTRUCTIONS = PASS
MINIO_REPRO_INSTRUCTIONS = PASS
MIGRATION_REPRO_INSTRUCTIONS = PASS

CURRENT_RELEASE_DOCUMENTATION = PASS
CURRENT_INPUT_SUPPORT_DOCUMENTATION = PASS
CURRENT_API_DOCUMENTATION = PASS
CURRENT_SECURITY_DOCUMENTATION = PASS
CURRENT_LIMITATIONS_DOCUMENTATION = PASS

DOCUMENTATION_INVENTORY_TOTAL = 1522
RELEASE_FACING_DOCUMENTS = 20
KNOWN_LIMITATIONS = 8
UNSUPPORTED_PUBLIC_CLAIMS = 0
KNOWN_LIMITATIONS_WITHOUT_DISCLOSURE = 0
BROKEN_RELEASE_DOC_LINKS = 0
PRIVATE_LOCAL_PATH_HITS = 0
SECRET_PATTERN_HITS = 0

TYPED_PHONON_BAND_IMPORT = SUPPORTED_WITH_LIMITS
TYPED_PHONON_DOS_IMPORT = SUPPORTED_WITH_LIMITS
GENERIC_PHONON_YAML_JSON = MAPPING_ONLY

REGISTRY = 62
DATAPROFILE = 2.4
ANALYSIS_INTENT = 1.0
ELIGIBILITY_RESOLUTION = 1.0
ANALYSIS_PLAN = 0.1 / 0.2
MIGRATION = 0007_phase10m1_workspace_domain
MAX_PANELS_PER_WORKSPACE = 32

CURRENT_FACT_MODEL_HASH = 92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a
FACT_MODEL_HASH_IMPACT_BY_PHASE13_3 = NO
CURRENT_SCOPE_BASELINE_HASH = bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba
SCOPE_BASELINE_HASH_IMPACT_BY_PHASE13_3 = NO
PHASE12_PRODUCT_BASELINE_HASH = 29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4

BACKEND = 1445 passed / 1 skipped / 51 integration deselected
FRONTEND = 460 passed
PHASE13_FOCUSED = 128 passed
SERVICE_BACKED = 50 passed / 0 skipped
CHROMIUM = PASS
FIREFOX = PASS
WEBKIT = PASS
MOBILE_390X844_RETAINED = PASS
LINUX_REPLAY = PASS
WINDOWS_REPLAY = PASS
TYPECHECK = PASS
BUILD = PASS
UV_LOCK_CHECK = PASS
GIT_DIFF_CHECK = PASS
SECURITY = PASS
SECRET_SCAN = PASS
MANIFEST_SELF_CHECK = PASS
npm audit = UNAVAILABLE_CONFIGURED_MIRROR_NOT_IMPLEMENTED

PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
NEW_SCIENTIFIC_TOOLS = 0
NEW_SCIENTIFIC_ALGORITHMS = 0
NEW_SCIENTIFIC_ADAPTERS = 0
NEW_ARTIFACT_FAMILIES = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_DEPENDENCIES = 0
LOCKFILE_CHANGES = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0

RELEASE_CRITICAL_INTEGRATION_DEFECTS = 0
SCIENTIFIC_DEFECTS = 0
SECURITY_DEFECTS = 0
UNCLASSIFIED_RELEASE_GAPS = 0

PHASE13_3_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_3_COMPLETION_RECORDED

PHASE_13 = IN_PROGRESS / DOCUMENTATION_AND_REPRODUCIBILITY_COMPLETE
PHASE_13_4 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_4_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-3 Queue Archive

Implementation exact-SHA CI `31703805747` and completion commit
`f4e2bb324ec4c248869cdc022f926d6f40448522` were verified before removing
the sole completed Phase 13-3 task block. The documentation and reproducibility
result remains permanently recorded above.

```text
PHASE13_3_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_3_COMPLETION_RECORDED
PHASE13_3_QUEUE_ARCHIVED

TASK_BLOCK_COUNT = 0
EXECUTABLE_PENDING_TASKS = 0

PHASE_13_4 = REVIEWER_GATE / AWAITING REVIEWER PROMPT
PHASE13_4_EXECUTABLE_TASK_CREATED = NO

INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-5 Final Regression + Release Acceptance Result

Status: PASS
Completed: 2026-08-14

The validation/evidence implementation `b60e048abbf366fdbd9fe72da27efd675fc50939`
passed exact-SHA CI `31728986993`. Seven newly created canonical user paths used
real PostgreSQL, Redis, MinIO, a fresh worker, registered adapters, persisted
artifacts, job-derived Workspaces, Chromium UI Finalize, Reports, and paired
non-executable Recipes. The run recorded 18 ToolCalls, 85 Artifacts, seven
Workspaces, seven finalized Reports, and seven Recipes; no fresh Artifact was
unreachable. No production, scientific, support, schema, dependency, migration,
or LLM-site change was made.

The retained negative, panel-cap, documentation/reproducibility, browser,
accessibility, performance, security, and Linux/Windows authority gates pass.
The sealed Fact hash is
`92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a`, the
sealed Scope hash is
`bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba`, the
Phase12 baseline is
`29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4`, and the
reproducibility-manifest semantic hash is
`931d6214cb11dbcad628f5b33ea97e043bbfeb54fbccc2f8c87cffebad9537e2`.

```text
PHASE_13_5 = PASS / FINAL_REGRESSION_AND_RELEASE_ACCEPTANCE_COMPLETE
PHASE13_5_RELEASE_ACCEPTANCE = PASS
RELEASE_CANDIDATE_ACCEPTED = YES
READY_FOR_PHASE13_6 = YES
PHASE13_5_FRESH_DEMOS_STARTED = 7
PHASE13_5_FULL_DEMOS_EXECUTED = 7
PHASE13_5_DEMO_PASS_OR_EXPLICIT_LIMIT = 7/7
P13X2_ACCEPTANCE = 8/8
UNREACHABLE_ARTIFACTS = 0
PANEL_TRUNCATION = 0
MAX_PANELS_PER_WORKSPACE = 32
TYPED_PHONON_BAND_IMPORT = SUPPORTED_WITH_LIMITS
TYPED_PHONON_DOS_IMPORT = SUPPORTED_WITH_LIMITS
GENERIC_PHONON_YAML_JSON = MAPPING_ONLY
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
INPUT_SUPPORT_PROMOTIONS = 0
PHASE13_5_VALIDATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_5_COMPLETION_RECORDED
PHASE_13_6 = REVIEWER_GATE / AWAITING_REVIEWER_PROMPT
PHASE13_6_EXECUTABLE_TASK_CREATED = NO
INITIAL_RELEASE_COMPLETE = NO
PHASE14_CREATED = NO
```

## Phase 13-6 Final Archive + Presentation Package Result

Status: PASS
Completed: 2026-08-14

Implementation/evidence SHA `48b270c6d2c6191b5707f6ee1c4d81a6ab9c8987`
passed exact-SHA CI `31768285019`. The final package freezes production surface
hash `11ffe1847ddffcf6b7a7d5f7d6286146910a19c4c89e018f3b8f47a0c4138151`,
InitialReleaseManifest semantic hash
`2f255942d4557569f7f01d6d1118a5cec1bc209f03bf1cf92b21d65fb65be844`,
and deterministic archive SHA-256
`3b328585f9345dda341a349f8745e4e3af89b6bb0a80e79747c03a52aa86bbbd`
(1,630,918 bytes; 45 entries). Extraction, manifest, link, traversal,
private-path, secret, and screenshot provenance checks pass.

Failed candidates remain retained: `ad0c98f4e469bb9215cd651ad6ed791527faf01c`
/ CI `31767331402` failed clean-checkout artifact ordering and was corrected by
`f7388b8ef402826d9a0f978c6c43f800449da5f3`; that SHA / CI `31767878567`
failed the retained sanitizer self-match and was corrected by the verified
implementation `48b270c6d2c6191b5707f6ee1c4d81a6ab9c8987`. Both are
`CI_EVIDENCE_PORTABILITY` history, not release builds.

```text
PHASE_13_6 = PASS / FINAL_ARCHIVE_AND_PRESENTATION_PACKAGE_COMPLETE
PHASE13_6_INITIAL_RELEASE_CLOSURE = PASS
PHASE13_6_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_6_COMPLETION_RECORDED
INITIAL_RELEASE_COMPLETION_RECORDED
PHASE_13 = COMPLETE / INITIAL_RELEASE_COMPLETE
INITIAL_RELEASE = COMPLETE / PHASE13_FINAL_ARCHIVE_AND_PRESENTATION_SEALED
INITIAL_RELEASE_COMPLETE = YES
KNOWN_LIMITATIONS = 8
KNOWN_LIMITATIONS_WITHOUT_DISCLOSURE = 0
P13X2_ACCEPTANCE = 8/8
CANONICAL_DEMOS_ACCEPTED = 7/7
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
INPUT_SUPPORT_CHANGES = 0
NEW_DEPENDENCIES = 0
NEW_DATABASE_MIGRATIONS = 0
NEW_LLM_CALL_SITES = 0
REAL_LLM_CALLS = 0
PHASE14_CREATED = NO
NEXT_EXECUTABLE_PHASE = NONE
```

## 2026-08-16 Phase D Attempt 2 - Controlled Resume

Status: BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED

Completed: 2026-08-16T00:25:15+08:00

Reviewer-authorized controlled placement resolved `PHASE_D-B001`: the
repository-root frozen ZIP was copied byte-for-byte to `_qualification/inputs/`
without moving or modifying the source. Source and destination are each
19,073,044 bytes with SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`,
and direct byte comparison passed.

The resumed package audit passed: root and all 16 case hash manifests have zero
mismatches, all required case structures/assets exist, canonical readiness is
16/16, Recipe execution authorization is 0/16, and paraphrase robustness remains
the frozen 7/16. The current Registry is version 0.1.0 with 62 Tools; repository
authority and qualification authority show no material contract drift.

The application shell loaded in the Codex in-app browser at 1280x720, basic Data
navigation worked, and no console warning/error was observed. DeepSeek policy
resolves to the allowed default model and `DEEPSEEK_KEY` is present; no live call
was made. Phase D remains blocked because PostgreSQL authentication fails,
Redis and MinIO are unavailable, a fresh worker cannot connect, the durable
backend runtime is unhealthy, and no safe fresh qualification namespace can be
verified. These are retained as `PHASE_D-B002` through `PHASE_D-B007`.

Evidence validation: 8 JSON files parsed, 9 SHA256SUMS entries self-validated,
secret/private-path scans returned zero hits, all case/LLM/Job/Artifact counters
are zero, frozen package hashes remain unchanged, and tracked production diff is
zero. Evidence is `_qualification/evidence/phase_d/attempt_02/`; Attempt 1 is
preserved at `_qualification/evidence/phase_d/attempt_01_blocked/`.

```text
PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED
READY_FOR_PHASE_E = NO
PHASE_D-B001 = RESOLVED
DATABASE_HEALTHY = NO
MIGRATION_AT_EXPECTED_HEAD = NO
QUEUE_BACKEND_HEALTHY = NO
OBJECT_STORAGE_HEALTHY = NO
BACKEND_HEALTHY = NO
FRONTEND_HEALTHY = YES
FRESH_WORKER_AVAILABLE = NO
BROWSER_APP_SHELL_ACCESSIBLE = YES
PROVIDER_CONFIGURATION_RESOLVES = YES
REQUIRED_PROVIDER_CREDENTIAL_PRESENT = YES
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
PHASE_E_EXECUTED = NO
```

## 2026-08-16 Phase E - Autonomous 16-Case Live-Agent Browser Qualification

Status: FAILED / BLOCKED_AUTHORITY_CONFLICT

Completed: 2026-08-16T04:51:17+08:00

Discovery used the frozen qualification ZIP with SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`.
Six repository-grounded routing/planning/interpretation corrections were made
as immutable local commits. Focused verification for the final correction
passed 38 AnalysisIntent, 32 capability Planner, and 34 natural-language
evidence tests; Ruff and `git diff --check` passed.

`Q-DATASET-001` completed the real Browser/DeepSeek/Planner/Queue/Worker/
Adapter/Artifact/Interpretation/Workspace/Report/Recipe discovery workflow on
candidate `8768f544956bf89b1fc1ccf51d6896e9221b3462`.

The campaign stopped at `Q-COMPOSITION-001` on candidate
`2d7f92d266c51a3401a36f619082e5840e0d60f9`. The frozen Case provides only a
CSV table but requires `structure_resource` and
`structure.composition_from_structure`, whose Registry contract requires a
periodic `Structure`. It also requires seven exact Tools/steps while current
AnalysisPlan and selection contracts cap the plan at four. Phase E requires all
expected Tools and explicitly mandates `BLOCKED_AUTHORITY_CONFLICT` for this
kind of contradiction. The package, CASE files, assets, and scientific values
were not changed.

Evidence:
`_qualification/evidence/phase_e/campaign_20260816_blocked_authority_conflict/`.
No final 16-case requalification, exact-SHA CI, completion lifecycle, or later
task was executed.

## 2026-08-16 Phase D - Autonomous Remediation, Requalification & Environment Seal

Status: PASS / LIVE_QUALIFICATION_ENVIRONMENT_SEALED

Completed: 2026-08-16T03:40:00+08:00

The committed D-R1 candidate exposed `PHASE_D-B009`: RQ's default Worker exits
on Windows when it consumes a queued job because `os.fork()` is unavailable.
Commit `54c66abc499c646dc27b612dbf28747b176177c8` adds the canonical
cross-platform worker entrypoint and regression tests. A real isolated Redis
execution smoke returned 42, while the final canonical worker stayed idle with
zero successful and failed qualification jobs.

Attempt 6 independently reverified ZIP SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`,
123 root entries, all 16 case manifests, canonical readiness 16/16, and the
declared paraphrase authority 7/16. PostgreSQL, Redis, MinIO, migration head
`0008_phase_d_r1_namespace`, a fresh base-to-head database, durable project
survival across backend restart, empty Workspace history, backend, frontend,
fresh Worker, provider configuration, and app-shell browser smoke all pass.

Validation: affected Python `67 passed, 2 skipped`; required service-backed
`51 passed, 0 required skips`; frontend `460 passed`; TypeScript typecheck and
production build pass; `uv lock --check`, Ruff, and `git diff --check` pass.
Attempt 6 evidence has 19 hashed entries with zero JSON, hash, secret,
private-path, zero-counter, package-mutation, or production-runtime-diff errors.
No push or CI run was required or performed.

```text
PHASE_D = PASS / LIVE_QUALIFICATION_ENVIRONMENT_SEALED
READY_FOR_PHASE_E = YES
FINAL_REPOSITORY_HEAD_SHA = 54c66abc499c646dc27b612dbf28747b176177c8
HEAD_EQUALS_ORIGIN_MASTER = NO
PHASE_D-B001..PHASE_D-B009 = RESOLVED
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
PRODUCTION_RUNTIME_AFFECTING_UNCOMMITTED_DIFFS = 0
BLOCKERS = []
```

## 2026-08-16 Phase D-R1 - Durable Namespace Migration / Bootstrap Remediation

Status: COMPLETED / DURABLE_NAMESPACE_MIGRATION_BOOTSTRAP_CORRECTED

Completed: 2026-08-16T02:31:30+08:00

Root cause was confirmed as SQLAlchemy/Alembic drift plus split Project
authority: migration 0007 lacked `users`, `organizations`, the canonical Project
foreign keys and index, while PostgreSQL-mode `POST /projects` still created only
process-local state. Forward migration `0008_phase_d_r1_namespace` now creates
and backfills the required schema, and PostgreSQL-mode Project create/list uses
`SqlAlchemyProjectRepository`.

Both isolated PostgreSQL migration paths passed: empty database to new head and
0007 to new head with an existing Project preserved and actor/organization rows
backfilled. Production API verification created Project
`project_4e11968a578b49d8ba165024`, resolved an empty Workspace history, and
reloaded both after backend process restart. Database Job, ToolCall, and Artifact
counts remained zero; no formal qualification case or LLM call ran.

Modified files: migration 0008; `durable_projects.py`; PostgreSQL-mode Project
wiring in `phase2_runtime.py`; migration/API/service regression tests; current
runtime/schema docs and persistent governance; focused evidence under
`_qualification/evidence/phase_d_r1/`.

Tests: 23 focused unit/API passed; 15 affected PostgreSQL/Redis/MinIO service
tests passed; 7 migration regressions passed; docs link, new-file ruff,
`uv lock --check`, `git diff --check`, JSON parse, evidence SHA256, secret scan,
private-path scan, and zero execution counters passed. A full backend observation
returned 1454 passed, 51 skipped, and 21 non-D-R1 failures: 19 stale historical
queue assumptions, one pre-existing Phase 13 raw-byte/CRLF manifest mismatch,
and one evidence link checked before generation; that link subsequently passed.

Commit/CI: not requested; HEAD remains
`08939f1b72ce37f153a0bdc18eee213f336b3636` with an uncommitted working tree.

```text
PHASE_D_R1 = PASS / DURABLE_NAMESPACE_MIGRATION_BOOTSTRAP_CORRECTED
NEW_MIGRATION_HEAD = 0008_phase_d_r1_namespace
FRESH_DB_BASE_TO_HEAD = PASS
PREVIOUS_HEAD_TO_NEW_HEAD = PASS
PROJECT_DURABLY_PERSISTED = PASS
PROJECT_SURVIVES_PROCESS_RESTART = PASS
WORKSPACE_HISTORY_PROJECT_RESOLUTION = PASS
MANUAL_DDL_WORKAROUND = 0
METADATA_CREATE_ALL_WORKAROUND = 0
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_PACKAGE_CHANGES = 0
PHASE_D_ATTEMPT_5_EXECUTED = NO
PHASE_E_EXECUTED = NO
```

## 2026-08-16 Phase D Attempt 3 - Docker Runtime Controlled Resume

Status: BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED

Completed: 2026-08-16T01:11:42+08:00

Docker Desktop is available through its installed CLI despite the inherited
Codex shell PATH not being refreshed. Docker Client/Engine are 29.7.2, Docker
Desktop is 4.86.0, and Compose is 5.3.1. The checked-in Compose configuration
parses successfully and defines project-scoped network and volume names for the
isolated `mdi-phase-d-attempt3` project. Its infrastructure services reference
`postgres:16-alpine`, `redis:7-alpine`, and `quay.io/minio/minio:latest`; no
application image build is required for this Phase D infrastructure startup.

Safe-isolation preflight failed before `compose up`: the checked-in file fixes
published host ports 5432 and 6379, already owned by non-Docker PostgreSQL and
Memurai services. Reviewer authorized preemption, but Windows denied both
service-control and direct-process termination from the current non-elevated
session. Existing services and data remained unchanged. No container, network,
volume, database, Redis state, MinIO bucket, backend, worker, or namespace was
partially created. The repository runbook provides local credential and MinIO
bucket bootstrap authority, so credentials are not retained as a separate
blocker.

The full frozen-package gate was independently repeated: external ZIP SHA-256
matches, root and 16 case manifests have zero mismatches, canonical readiness is
16/16, report/Recipe readiness is 16/16, Recipe execution authorization is 0,
and paraphrase robustness remains 7/16. Worktree classification found zero
runtime-affecting tracked changes: governance/docs are non-production, one
tracked test file is TEST_ONLY, and global worktree cleanliness remains NO.

Evidence validation: 10 JSON files parsed, 11 SHA256SUMS entries self-validated,
secret/private-path scans returned zero hits, and all case/LLM/Job/Artifact
counters remain zero. Attempt 3 evidence is retained at
`_qualification/evidence/phase_d/attempt_03/`; Attempts 1 and 2 remain intact.

```text
PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED
READY_FOR_PHASE_E = NO
PHASE_D-B001 = RESOLVED
PHASE_D-B008 = COMPOSE_FIXED_HOST_PORTS_NOT_AVAILABLE
DOCKER_COMMAND_AVAILABLE = YES
DOCKER_ENGINE_REACHABLE = YES
DOCKER_COMPOSE_AVAILABLE = YES
SAFE_ISOLATED_COMPOSE_RUNTIME = NO
COMPOSE_UP_EXECUTED = NO
GLOBAL_WORKTREE_CLEAN = NO
TRACKED_PRODUCTION_RUNTIME_WORKTREE_CLEAN = YES
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
PHASE_E_EXECUTED = NO
```

## 2026-08-14 Phase A Repository Capability Census

Status: PASS / REPOSITORY_CAPABILITY_CENSUS_COMPLETE

Completed: 2026-08-14 16:08:45 +08:00

The repository-grounded census package is retained at
`docs/qualification/phase_a_repository_capability_census/`. It inventories 4
user entry paths, 15 format families, 15 semantic data kinds, 18 user capability
families, all 62 Registry Tools, 42 Artifact/renderer declarations, and 36
user-centric qualification cases. The 16-case minimum set covers all 20 current
supported or supported-with-limits input combinations; the complete catalog
gives all 47 current Planner-visible Tools case participation. Three phonon-animation
Artifacts/renderers lack an executable normal-user case because eigenvector
entry remains mapping-only; the exact boundary and the absent inline-upload
request caps are retained among eight P2 qualification-design gaps.

Validation: Phase A focused `7 passed`; targeted Registry/parser/Profile/current
authority `94 passed` with four existing CIF warnings; renderer registry `4
passed`. Two generator runs produced identical package hash
`cd6caf371e4b0f0ef2364b0a485c043287467e9a141782506ce6b52418bf46c0`.
Manifest hash/size, repository evidence refs, internal links, UTF-8/LF,
private-path, secret-pattern, Python compile, and diff checks pass. An earlier
test-only candidate failed collection due to indentation while extending queue
vocabulary; it was corrected before the successful 94-test run.

No web access, external fixture download, browser qualification, live LLM call,
production code change, scientific behavior change, input-support change,
Registry/parser/Adapter/renderer/API behavior change, commit, push, or exact-SHA
CI occurred. Initial Release remains complete and Phase 13 remains sealed.

```text
PHASE_A = PASS / REPOSITORY_CAPABILITY_CENSUS_COMPLETE
QUALIFICATION_DATA_RESEARCH_READY = YES
AUTHORITY_CONFLICTS = 0
QUALIFICATION_DESIGN_GAPS = 8
PHASE_B_EXTERNAL_DATA_RESEARCH_EXECUTED = NO
PHASE_B_EXTERNAL_DATA_DOWNLOADED = 0
PRODUCTION_CODE_CHANGES = 0
SCIENTIFIC_BEHAVIOR_CHANGES = 0
REAL_LLM_CALLS = 0
INITIAL_RELEASE_COMPLETE = YES
PHASE14_CREATED = NO
```

## Phase 13-6 Queue Archive

Implementation/evidence `48b270c6d2c6191b5707f6ee1c4d81a6ab9c8987`
passed exact-SHA CI `31768285019`, and completion commit
`7159e0c16de514b73524ef158d6761897d94cf31` was pushed before removing the
sole completed Phase13-6 task block. The final release package and completion
record remain permanently retained.

```text
PHASE13_6_IMPLEMENTATION_VERIFIED_BY_EXACT_SHA_CI
PHASE13_6_COMPLETION_RECORDED
PHASE13_6_QUEUE_ARCHIVED
INITIAL_RELEASE_COMPLETION_RECORDED
TASK_BLOCK_COUNT = 0
EXECUTABLE_PENDING_TASKS = 0
PHASE14_CREATED = NO
NEXT_EXECUTABLE_PHASE = NONE
```

## 2026-08-16 Phase D Attempt 4 - Complete Live Qualification Environment Seal

Status: BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED

Completed: 2026-08-16T01:43:24+08:00

The frozen repository and qualification identities were independently
reverified at HEAD `08939f1b72ce37f153a0bdc18eee213f336b3636` and ZIP SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`.
Root and all 16 case hash manifests have zero mismatches, canonical readiness is
16/16, and paraphrase robustness remains the declared 7/16.

The unmodified Compose authority started PostgreSQL, Redis, and MinIO in the
isolated `mdi-phase-d-attempt4` project. All three containers are healthy;
their immutable image IDs and RepoDigests, isolated volume identities, and
network identity are retained. PostgreSQL connectivity and Alembic head 0007,
Redis `mdi-jobs`, the empty `mdi-artifacts` bucket, current-SHA backend durable
health, fresh idle RQ worker, frontend, DeepSeek configuration presence, and the
browser app shell all passed. The queue and durable Job/ToolCall/Artifact counts
remain zero.

The only remaining blocker is `PHASE_D-B007`. A fresh project created through
the normal `POST /projects` surface is process-local, while Workspace history
uses the durable SQL repository. The official Alembic 0007 migration path does
not create `users` or `organizations`; canonical
`SqlAlchemyProjectRepository.save()` consequently fails with an undefined
`users` table and Workspace history returns typed `PROJECT_NOT_FOUND`. The
historical release harness works around this with hand-written DDL, but Phase D
correctly did not treat that test harness or `metadata.create_all` as production
migration authority.

Changed files are limited to Phase D governance and local qualification work /
evidence. Attempts 1-3 were preserved. Validation: 12 JSON files parsed; 13
`SHA256SUMS.txt` entries self-validated; secret and private-path scans passed;
production runtime tracked diffs are zero; all formal case, Job, Artifact, and
real-LLM counters are zero. No commit, push, or CI run was requested or executed.

```text
PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_SEALED
READY_FOR_PHASE_E = NO
PHASE_D-B001 = RESOLVED
PHASE_D-B002 = RESOLVED
PHASE_D-B003 = RESOLVED
PHASE_D-B004 = RESOLVED
PHASE_D-B005 = RESOLVED
PHASE_D-B006 = RESOLVED
PHASE_D-B007 = UNRESOLVED
PHASE_D-B008 = RESOLVED
DATABASE_HEALTHY = YES
MIGRATION_AT_EXPECTED_HEAD = YES
QUEUE_BACKEND_HEALTHY = YES
OBJECT_STORAGE_HEALTHY = YES
BACKEND_HEALTHY = YES
FRONTEND_HEALTHY = YES
FRESH_WORKER_AVAILABLE = YES
BROWSER_APP_SHELL_ACCESSIBLE = YES
FRESH_QUALIFICATION_NAMESPACE_READY = NO
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
PHASE_E_EXECUTED = NO
```

## 2026-08-16 Phase B/C-R1 - Qualification Authority Reconciliation, Contract Repair and Refreeze

Status: COMPLETED / QUALIFICATION_AUTHORITY_RECONCILED_AND_REFROZEN

Completed: 2026-08-16T09:31:27+08:00

The historical package remains byte-identical at SHA-256
`3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`
and is retained as superseded execution history. The separately versioned
`Phase_BC_R1_Qualification_Authority_Reconciled.zip` uses schema
`PhaseBClosurePhaseCContractManifest/1.1`, has SHA-256
`6a1e3f1100407fd70f2d689bb2022754ac3723f8c127c8963042b25db82dc3b3`,
contains 129 sorted entries and 19,102,189 bytes, and reproduced the same SHA in
two independent deterministic builds.

All 16 primary Cases were audited against repository candidate
`2d7f92d266c51a3401a36f619082e5840e0d60f9`, Registry 62 / snapshot
`registry_371aa3f8106e863af9c7c648`, AnalysisIntent 1.0,
EligibilityResolution 1.0, AnalysisPlan 0.1/0.2, ToolPlannerMetadata 1.0,
migration `0008_phase_d_r1_namespace`, and both four-step planning caps.
`Q-COMPOSITION-001` no longer requires a periodic-Structure Tool from CSV-only
assets. The 16-case result is 15 supported analyses plus one expected typed
pre-Plan rejection for non-periodic XYZ viewer execution. Maximum required
Tools per turn is 4/4.

The primary campaign now distinguishes 33 required Tool assertions from 45/47
Planner-available Tool coverage potential. Seventeen capability families, 35
Artifact types and 13 renderer contracts have primary potential. The two honest
supplemental Tool gaps are `phonon.animation` and
`structure.composition_from_structure`; they were not forced into the primary
Cases. Campaign association remains non-qualifying until later live observation.

The new static validator passes on both the staging tree and a clean ZIP
extraction. Root and all 16 case manifests have zero missing files and zero hash
mismatches. Protected `SOURCE_*`, `UPLOAD_*`, `LICENSE.txt`, and
`PROVENANCE.json` bytes are unchanged. The evidence manifest, JSON parse,
UTF-8/LF, secret, private-path, and zero-execution checks pass.

Validation: focused R1 `7 passed`; Ruff and Python compile PASS. The complete
non-integration CI command also ran: `1471 passed, 20 failed, 1 skipped, 52
deselected`. Nineteen failures are historical tests that hard-code obsolete
`TASKS.md` queue cardinality/content, and one is a pre-existing Phase13-4
evidence byte-size mismatch in the dirty entry worktree. No R1 or production
runtime assertion failed; historical sealed evidence was not rewritten.

Modified files: three non-production R1 scripts, one focused test, the new
versioned package and R1 evidence, qualification navigation, persistent
governance, `TASKS.md`, and this append-only result. Production runtime,
scientific behavior, support dispositions, dependencies, lockfiles, and the old
package were not changed.

```text
PHASE_BC_R1 = PASS / QUALIFICATION_AUTHORITY_RECONCILED_AND_REFROZEN
CASES = 16
EXECUTION_READY_CASES = 16/16
CASE_AUTHORITY_CONFLICTS = 0
REQUIRED_TOOL_INPUT_MISMATCHES = 0
MISSING_REQUIRED_COMPANION_ASSETS = 0
REQUIRED_TOOL_COUNT_OVER_PLAN_CAP = 0
UNSUPPORTED_TOOL_REQUIRED_AS_EXECUTABLE = 0
MAPPING_ONLY_REQUIRED_AS_EXECUTABLE = 0
REQUIRED_ARTIFACT_WITHOUT_PRODUCER = 0
REQUIRED_RENDERER_WITHOUT_ARTIFACT = 0
STATIC_EXECUTABLE_CONTRACT_VALIDATOR = PASS
ROOT_HASH_MISMATCHES = 0
CASE_HASH_MISMATCHES = 0
OLD_PACKAGE_MUTATIONS = 0
SCIENTIFIC_VALUE_FABRICATION = 0
UNIT_GUESSING = 0
STRUCTURE_INFERENCE_FROM_FORMULA = 0
SUPPORT_SURFACE_EXPANSION = 0
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_CASE_EXECUTIONS = 0
PHASE_E_CONTINUED = NO
```

Commit/CI status: no commit, push, or CI lifecycle was requested or executed.

## 2026-08-16 Phase B/C-R1.1 - Minimal Qualification Authority Hygiene Correction

Status: COMPLETED / QUALIFICATION_AUTHORITY_INTERNALLY_CONSISTENT_AND_REFROZEN

Completed: 2026-08-16T09:57:47+08:00

The historical R1 package remains byte-identical at SHA-256
`6a1e3f1100407fd70f2d689bb2022754ac3723f8c127c8963042b25db82dc3b3`.
The separately versioned
`Phase_BC_R1_1_Qualification_Authority_Reconciled.zip` has SHA-256
`bf1198f0281119af6b0485518ace053d99e827d0ed3d31d077ddf94ed8d4f87f`,
contains 132 sorted entries and 19,105,576 bytes, and reproduced the same SHA
in two independent deterministic builds.

Repository/package governance established that `requiredReportBehavior`,
`requiredRecipeBehavior`, and `requiredLimitations` are canonical. The retained
`expectedReport`, `expectedRecipe`, and `expectedLimitationAssertions` fields
remain normative compatibility aliases and now exactly mirror their canonical
fields in all 16 Cases. The sole source contradiction was corrected in
`Q-ATOMIC-VIEW-001`; it remains an `EXPECTED_REJECTION` with no Plan, Job,
ToolCall, Artifact, Report, or Recipe expected.

All 16 Cases pass report/recipe/limitation alias comparison, execution-turn
Tool-union comparison, required Tool count, per-turn four-step Plan-cap, and
expected-rejection checks. The six R1 multi-turn scenarios remain unchanged.
Package-level machine-readable authority now states that multi-turn Planner
submissions use ordered `executionTurns[].question`, single-turn Cases use the
sole turn question, and expected rejection submits the canonical question and
must stop before Plan creation. Campaign coverage remains 33 required Tool
assertions, 45/47 primary potential Tools, and two supplemental candidates.

The static validator now detects conflicting report, Recipe, and limitation
requirements; execution-turn Tool-union mismatch; required Tool count mismatch;
and execution requirements attached to expected rejection. The historical R1
tree fails exactly once with `CONFLICTING_REPORT_REQUIREMENTS`; the R1.1 staging
tree and clean extracted package both pass with zero issues. Root/case manifests
have zero missing files and zero hash mismatches. `SOURCE_*`, `UPLOAD_*`,
`PROVENANCE.json`, and `LICENSE.txt` bytes are unchanged; scientific values,
units, wavelength, q-path, uncertainty, structure inference, support surface,
production runtime, live LLM calls, and formal qualification execution all have
zero changes/executions.

Validation: Ruff PASS; focused R1/R1.1 `16 passed`; JSON parse, evidence SHA
self-check, and secret-pattern scan PASS. Full non-integration regression was
reproduced as `1480 passed, 20 failed, 1 skipped, 52 deselected`. The 20 failures
match the prior disclosed classification: 19 obsolete historical tests that
hard-code old `TASKS.md` queue content/cardinality and one pre-existing
Phase13-4 evidence byte-size mismatch. No R1/R1.1 or production-runtime test
failed, and the full repository suite is not claimed as PASS.

Modified files: non-production R1/R1.1 qualification scripts and focused tests,
the separately versioned package and evidence, qualification schema/navigation,
persistent governance, `TASKS.md`, and this append-only result. Phase D and
Phase E were not started.

```text
PHASE_BC_R1_1 = PASS / QUALIFICATION_AUTHORITY_INTERNALLY_CONSISTENT_AND_REFROZEN
CASES = 16
EXECUTION_READY_CASES = 16/16
CASE_AUTHORITY_CONFLICTS = 0
CROSS_FIELD_CONTRACT_CONFLICTS = 0
Q_ATOMIC_VIEW_EXPECTED_REJECTION_CONSISTENT = YES
EXECUTION_TURN_TOOL_UNION_MISMATCHES = 0
REQUIRED_TOOL_COUNT_MISMATCHES = 0
REQUIRED_TOOL_COUNT_OVER_PLAN_CAP = 0
EXPECTED_REJECTION_EXECUTION_CONTRADICTIONS = 0
STATIC_EXECUTABLE_CONTRACT_VALIDATOR = PASS
CROSS_FIELD_CONSISTENCY_VALIDATOR = PASS
ROOT_HASH_MISMATCHES = 0
CASE_HASH_MISMATCHES = 0
PROTECTED_SCIENTIFIC_BYTE_CHANGES = 0
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_EXECUTIONS = 0
READY_FOR_PHASE_D_RESEAL = YES
READY_FOR_PHASE_E_DIRECT_CONTINUATION = NO
```

Commit/CI status: no commit, push, or CI lifecycle was requested or executed.

## 2026-08-16 Phase D R1.1 - Live Qualification Environment Re-Seal

Status: FAILED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_RESEALED

Completed: 2026-08-16T10:31:44+08:00

The R1.1 package at SHA-256
`bf1198f0281119af6b0485518ace053d99e827d0ed3d31d077ddf94ed8d4f87f`
was independently verified: 16 Cases, 15 analysis-execution Cases, one expected
pre-Plan rejection, 26 declared execution turns, zero root hash mismatches, and
zero case hash mismatches. The static executable-contract and cross-field
consistency validators both passed against current repository authority at
`2d7f92d266c51a3401a36f619082e5840e0d60f9`.

The repository-approved PostgreSQL, Redis, and MinIO containers were healthy.
A new database reached migration head `0008_phase_d_r1_namespace` through the
official Alembic chain. The current-SHA backend, frontend, fresh idle Worker,
DeepSeek configuration, browser app shell, and an empty durable project/
Workspace namespace all passed. The project survived a backend process restart;
Jobs, ToolCalls, Artifacts, Reports, Recipes, and Workspaces remained zero.

The re-seal stopped on three newly confirmed frozen-authority conflicts:

- `PHASE_D_R11_AUTH_001`: `Q-ARCHIVE-001` declares execution-ready UI ZIP
  upload, but the generic UI reads the ZIP with `File.text()` and the backend
  writes UTF-8 text. A mechanical round trip changed 10,912 source bytes into
  19,470 bytes and changed SHA-256.
- `PHASE_D_R11_AUTH_002`: `Q-XRD-001` requires CIF plus experimental-XRD
  companions in one dataset, while the generic normal-user UI submits one file.
- `PHASE_D_R11_AUTH_003`: `Q-ELECTRONIC-001` requires Band plus DOS companions
  in one dataset, while the same UI path submits one file.

These are not ordinary Phase D runtime defects. Implementing binary or generic
multi-resource upload would change the normal-user scientific input contract,
which is an explicit hard stop requiring authority reconciliation and refreeze.
No such product change was made.

Validation: focused tests `17 passed`; package/root/case hashes PASS; JSON parse,
evidence SHA-256 self-check, secret scan, private-path scan, and zero-execution
counter checks PASS. Evidence is preserved at
`_qualification/evidence/phase_d/attempt_07_r1_1_reseal_blocked_authority_conflict/`.

```text
PHASE_D = BLOCKED / LIVE_QUALIFICATION_ENVIRONMENT_NOT_RESEALED
READY_FOR_PHASE_E = NO
CASE_AUTHORITY_CONFLICTS = 3
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
```

Modified files: Phase D Attempt 7 evidence, `TASKS.md`, and this append-only
result. Historical Phase D/Phase E evidence and failed tasks remain unchanged.
Phase E-R1.1 was not created or started.

Commit/CI status: no commit, push, or CI execution was performed because Phase D
ended at the frozen-authority hard stop.

## 2026-08-16 Phase D-R2 - Normal-User Input Transport Contract Closure + R1.2 Refreeze

Status: FAILED / REVIEWER_AUTHORITY_DECISION_REQUIRED

Completed: 2026-08-16T10:53:23+08:00

The mandatory pre-change support audit classified `Q-ARCHIVE-001` and
`Q-ELECTRONIC-001` as already-supported resources blocked only by normal-user
transport defects. `Q-XRD-001` is different: its frozen experimental resource
declares `1.9373 angstrom`, while the current released `structure.xrd` path is
CuKa-only at `1.54184 angstrom`. Worker execution preflight and the experimental
comparison Adapter both require compatible wavelengths and prohibit silent
reprojection. The frozen Case nevertheless requires both `structure.xrd` and
`structure.experimental_xrd_comparison` as an execution-ready path.

This is a qualification-authority conflict that cannot be corrected through
byte-safe or multi-resource transport. Per task rules, remediation stopped for
Reviewer decision. A preliminary transport draft was completely reverted;
production runtime changes, package changes, scientific fixture changes,
formal qualification executions, Jobs, Artifacts, and real LLM calls are all
zero.

Validation: `uv run pytest tests/test_phase10n3_experimental_xrd.py -q` passed
(`10 passed`), including typed mismatch rejection. The R1.1 package SHA-256
remained `bf1198f0281119af6b0485518ace053d99e827d0ed3d31d077ddf94ed8d4f87f`.
Blocker evidence and a self-hashed manifest are preserved at
`_qualification/evidence/phase_d_r2/attempt_01_blocked_authority_conflict/`.

```text
PHASE_D_R2 = BLOCKED / REVIEWER_AUTHORITY_DECISION_REQUIRED
BLOCKER = PHASE_D_R2_AUTH_001
Q_ARCHIVE_CLASS = ALREADY_SUPPORTED_RESOURCE_BUT_INPUT_TRANSPORT_DEFECT
Q_ELECTRONIC_CLASS = ALREADY_SUPPORTED_RESOURCE_BUT_INPUT_TRANSPORT_DEFECT
Q_XRD_CLASS = AUTHORITY_AMBIGUOUS
READY_FOR_PHASE_BC_R1_2_REFREEZE = NO
READY_FOR_PHASE_D_RESEAL = NO
READY_FOR_PHASE_E = NO
PRODUCTION_CODE_CHANGES = 0
QUALIFICATION_PACKAGE_CHANGES = 0
SCIENTIFIC_FIXTURE_CHANGES = 0
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_EXECUTIONS = 0
```

Commit/CI status: no commit, push, or CI was performed because the task stopped
at its mandatory qualification-authority gate.

## Phase D-R2.1 - Reviewer XRD Authority Resolution + Normal-User Input Transport Closure + R1.2 Refreeze

Status: completed

Completion time: 2026-08-16T14:09:02+08:00

The normal-user transport defect is corrected by committed candidate
`657d3f88849b4d561ebd3aca0a648667049306fc`: browser uploads use exact File/Blob
bytes, the backend verifies declared SHA-256 and byte size before materializing
raw bytes, and bounded multi-resource bundles publish atomically into one
dataset with parser/contract-based roles rather than file-order semantics.

Reviewer XRD Branch B1 remains unchanged. R1.2 replaces only the stale 1.9373
angstrom qualification fixture with real Figshare hydroxyapatite measurements
whose source instrument record declares Cu and `ActuallyUsedLambda=1.54184`,
paired with public-domain COD 4317043 hydroxyapatite. The old data were not
relabeled, reprojected, or synthesized. All other 15 Case directories are
byte-identical to R1.1.

The deterministic R1.2 package is
`_qualification/inputs/Phase_BC_R1_2_Qualification_Authority_Reconciled.zip`,
SHA-256 `187816077abdc154ad8b8c86f30af37ad4a6a66ed5471c52a2c3ed1a8f4bedc2`,
19,222,448 bytes and 138 sorted entries. Two builds matched; root/case hash
mismatches and missing files are zero; static and extracted validators PASS.

Validation: backend focused `57 passed`; frontend `460 passed`, typecheck PASS,
build PASS with existing bundler warnings; qualification/transport focused
`30 passed` with four benign pymatgen CIF warnings. Full repository suite PASS
is not claimed. Production remediation is committed locally, not pushed, and no
remote CI is claimed. Real LLM calls, formal qualification executions, Jobs,
Artifacts, and Phase E executions remain zero. Evidence is at
`_qualification/evidence/phase_d_r2_1/`.

## Phase D-R2.1 Final Candidate Correction

Status: completed

Completion time: 2026-08-16T15:27:41+08:00

The complete Phase D re-seal found that a durable SQL Project remained visible
after API restart, but upload-session creation still checked only the restarted
process's local Project projection. The authorized transport closure now
rehydrates only an exact existing PostgreSQL Project before opening the bounded
upload transaction. Unknown Projects remain rejected.

The final product candidate is
`51e45c9436bef73f0c8ea1ccc5eb681dba1d21b8`. R1.2 was deterministically
refrozen against that exact candidate as SHA-256
`7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04`,
19,222,447 bytes and 138 sorted entries. Root/case mismatches and missing files
are zero; R1.1 remains unchanged. This correction changes no scientific,
Registry, support-disposition, Planner, Artifact, Renderer, Report, or Recipe
authority.

## Phase D R1.2 - Complete Live Qualification Environment Re-Seal

Status: completed / PASS

Completion time: 2026-08-16T15:27:41+08:00

The environment was sealed against product SHA
`51e45c9436bef73f0c8ea1ccc5eb681dba1d21b8` and R1.2 package SHA-256
`7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04`.
The package has 16 Cases, zero root/case hash mismatches, and PASS results for
static executable, cross-field, entry-path, and CuKa compatibility validators.

Fresh Docker-network runtime checks passed for Alembic base-to-head and repeated
upgrade at `0008_phase_d_r1_namespace`, PostgreSQL, Redis, MinIO, current-SHA
API, current-SHA fresh worker, provider configuration, and an empty durable
qualification namespace. The Project survived API process restart and Workspace
history returned an empty contract-valid result.

Actual Chrome 151 uploaded the frozen Archive, CuKa XRD/Structure, and
Electronic Band/DOS inputs through the product UI. Browser bytes, frozen bytes,
server receipts, and independent MinIO reads matched for all five files. XRD
and Electronic companions were persisted in their respective same Dataset with
no file-order role authority. A page reload re-enumerated all three Datasets.
No console, page, or startup network error was observed.

Validation: focused backend/qualification/namespace `35 passed`; service-backed
container-network namespace `1 passed`; frontend `460 passed`; typecheck PASS;
build PASS with the existing Plotly/glslify warning. JSON parse, evidence
SHA-256 self-check, secret scan, private-path scan, and zero-execution checks
PASS. Evidence is under
`_qualification/evidence/phase_d/attempt_08_r1_2_reseal/`.

```text
PHASE_D = PASS / LIVE_QUALIFICATION_ENVIRONMENT_RESEALED
READY_FOR_PHASE_E = YES
PHASE_D_R11_AUTH_001 = RESOLVED_BY_PRODUCT_TRANSPORT_FIX
PHASE_D_R11_AUTH_002 = RESOLVED_BY_PRODUCT_MULTI_RESOURCE_FIX
PHASE_D_R11_AUTH_003 = RESOLVED_BY_PRODUCT_MULTI_RESOURCE_FIX
REAL_LLM_CALLS = 0
FORMAL_QUALIFICATION_EXECUTIONS = 0
QUALIFICATION_JOBS_RUN = 0
QUALIFICATION_ARTIFACTS = 0
BLOCKERS = []
```

Commit/CI status: the final candidate is committed locally; no push or remote CI
is claimed or required by this Phase D task. Phase E was not created or started.

## Phase E-R1.2 — Canonical Live-Agent Browser Qualification Restart

Status: failed / `BLOCKED_AUTHORITY_CONFLICT`

Completion time: 2026-08-16T16:48:44+08:00

The R1.2 package was independently reverified at SHA-256
`7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04`.
The fresh discovery campaign completed Q-DATASET-001. Q-COMPOSITION-001 first
failed because composition-only "materials table" wording was promoted to
dataset overview; the minimal Intent/Planner correction is committed as
`610de07887d7c221e377bc1d8d01882df9d5a6d2`, passed 88 focused tests, and the
Case then passed all three fresh Browser/DeepSeek execution turns.

Q-TABLE-001 reached a genuine frozen-authority contradiction. Its R1.2 contract
requires material-property-bound `table.numeric_summary`, `viz.histogram`,
`viz.correlation`, and `viz.scatter`, while the declared normal-user CSV produces
zero `material_property` columns and exposes no semantic mapping entry. The real
Planner therefore selected forbidden `dataset.materials_explorer`; changing the
DataProfile/ToolPlannerMetadata contract or frozen Case is qualification-relevant
authority drift and was not performed.

Validation: Q-DATASET and Q-COMPOSITION are `PASS_DISCOVERY`; Q-TABLE is
`BLOCKED_AUTHORITY_CONFLICT`; 23 real LLM calls are recorded across preserved
attempts; no provider fallback or fixture/package mutation occurred. Evidence
contains 170 valid JSON files and a 220-entry SHA256SUMS manifest with zero
mismatches, secret hits, or private-path hits. Final exact-SHA CI, final Phase D,
and final 16-Case requalification were not started after the hard stop.

Evidence: `_qualification/evidence/phase_e_r1_2/discovery_20260816_01/`.
Minimum Reviewer action: reconcile Q-TABLE-001 by supplying an already-authorized,
provenance-preserving material-property mapping/fixture, or revise its frozen
execution contract to the repository's generic-tabular authority.

Commit/CI status: local remediation commit
`610de07887d7c221e377bc1d8d01882df9d5a6d2`; not pushed; remote exact-SHA CI not
run because the qualification hard stop occurred before final-candidate closure.

## Phase B/C-R1.4 — Q-TABLE Explicit Property-Target Authority Reconciliation

Status: failed / `PHASE_BC_R1_4 / QUALIFICATION_AUTHORITY_CONFLICT`

Completion time: 2026-08-16T18:20:00+08:00

The R1.4 non-production preflight retired qualification-only digest gating and
used content/provenance inspection plus current parser, DataProfile,
deterministic Intent, Eligibility, exact binding, and plan-cap paths. It made
zero real LLM calls and created zero formal qualification Jobs or Artifacts.
The historic R1.2 package and failed R1.3 evidence were preserved.

The real CC BY 4.0 JARVIS candidate correctly exposes `formation_energy`,
`band_gap`, and `density` as current material properties. With explicit natural
questions, numeric summary and correlation bind, but histogram and scatter
remain unbound because deterministic Intent supplies no material-property
targets. The all-16 audit also found deterministic ML target-semantic failures
for Q-ML-REG/UNC/CLASS, direct XRD comparison ineligibility, trajectory import
failure (`TRAJECTORY_NESTING_LIMIT_EXCEEDED`), and typed phonon failures
(`PHONON_SPECIES_ORDER_INVALID`). Therefore no R1.4 package was produced and
Phase D was not started.

Evidence: `_qualification/evidence/phase_bc_r1_4/attempt_01_authority_preflight/`.
Tests: the preflight completed twice consistently; 14 JSON evidence files parse;
the evidence has no active qualification integrity-key fields or checksum files;
no Phase E execution occurred.

## Phase B/C-R1.3 — Q-TABLE-001 Fixture Replacement and Binding Preflight

Status: failed / `PHASE_BC_R13_AUTH_001 / BLOCKED_AUTHORITY_CONFLICT`

Completion time: 2026-08-16T17:52:17+08:00

R1.3 preserved the R1.2 package at SHA-256
`7a77b1db55c93454b97914bae3ee9d30e0f08ccc38bfd986c5907f65e38d1d04` and
mechanically audited the current production Profile, deterministic Intent,
Eligibility, and ToolPlannerMetadata binding path. A real JARVIS-DFT-3D
candidate from Figshare DOI `10.6084/m9.figshare.6815699.v11` (CC BY 4.0)
produced three accepted material-property columns: `formation_energy`,
`band_gap`, and `density`. It therefore resolves the old fixture's Profile
defect, but cannot satisfy the frozen execution contract: the numeric summary,
distribution, and correlation turns are `INTENT_NOT_RECOGNIZED`; the scatter
turn has no target semantics and two unbound scalar property parameters.

Changing that outcome would require a frozen turn-contract revision or a
separately authorized normal-user property-target selection capability. Both
are outside this fixture-only task. No R1.3 ZIP, Phase D re-seal, or Phase E
execution was started. Evidence is in
`_qualification/evidence/phase_bc_r1_3/attempt_01_blocked_authority_conflict/`.

Tests: deterministic preflight rerun matched; focused Intent/Planner tests
passed `74 passed`; evidence JSON, SHA256SUMS, secret scan, private-path scan,
and zero-execution counters passed. The first pytest invocation lacked the
repository `PYTHONPATH` and failed during collection; the correctly configured
rerun passed. `REAL_LLM_CALLS=0`, formal qualification executions/jobs/artifacts
are zero. No commit or remote CI is claimed.

## Phase B/C-R1.4 — Final Result

Status: failed / `PHASE_BC_R1_4 / QUALIFICATION_AUTHORITY_CONFLICT`

Completion time: 2026-08-16T19:10:11+08:00

The content-and-contract preflight completed all 16 Cases and 26 analysis
turns with `REAL_LLM_CALLS=0`, zero formal qualification executions, Jobs, and
Artifacts. It passes 9 Cases and blocks 7: Q-TABLE explicit histogram/scatter
target binding; deterministic ML readiness for REG/UNC/CLASS; XRD direct
comparison dependency eligibility; trajectory parsing at the nesting limit;
and typed phonon species-order validation. The old R1.2 Q-TABLE fixture also
reproduces its historical material-property readiness failure.

No R1.4 package was created, no Phase D re-seal was started, and Phase E remains
unstarted. The focused Intent/Planner suite passed `74 passed`; the broader
entry-slice command reported `83 passed, 2 errors` from its existing all-seven
ready assertion and is not claimed green. Evidence JSON parsing, secret scan,
private-path scan, zero-execution counter validation, and the no-active-
qualification-checksum-file policy check passed. Evidence:
`_qualification/evidence/phase_bc_r1_4/attempt_01_authority_preflight/`.

## Phase B/C-R1.5 — Comprehensive Qualification Authority and Executability Reconciliation

Status: failed / `PHASE_BC_R1_5 / QUALIFICATION_AUTHORITY_CONFLICT`

Completion time: 2026-08-16T20:08:17+08:00

R1.5 classified all seven R1.4 blockers before correction. It closed the three
ML representation/question paths, modeled XRD's same-Plan theoretical-artifact
dependency, repaired the bounded trajectory validator's numeric-array scanner
defect, verified the phonon ordering metadata path, and corrected the stale
seven-demo entry-slice expectation. The fresh deterministic preflight passes
15 of 16 Cases across all 26 declared analysis turns.

The remaining blocker is `Q-TABLE-001`. The verified JARVIS candidate exposes
the approved `formation_energy`, `band_gap`, and `density` facts, but the
released non-ML normal-user Intent contract emits no exact material-property
target semantics. Required `viz.histogram` and `viz.scatter` bindings therefore
cannot be completed without a Reviewer decision on a qualification-relevant
product contract. No target guessing, semantic expansion, fixture fabrication,
or Tool metadata relaxation was used.

Tests: trajectory/parser/entry-slice `53 passed, 4 warnings`; Intent/Planner/
entry-slice `85 passed, 4 warnings`. The prior `83 passed, 2 errors` entry-slice
failure is resolved with no skipped or deleted test. No R1.5 authority package,
Phase D re-seal, or Phase E execution was created. `REAL_LLM_CALLS=0` and all
formal qualification Jobs, ToolCalls, and Artifacts are zero. Evidence:
`_qualification/evidence/phase_bc_r1_5/`.

## Q-TABLE Explicit Material-Property Target Intent Closure + Phase B/C-R1.6 + Phase D Re-Seal

Status: completed / `PHASE_BC_R1_6 = PASS / QUALIFICATION_AUTHORITY_PRODUCT_INTENT_ALIGNED_AND_REFROZEN`; `PHASE_D = PASS / LIVE_QUALIFICATION_ENVIRONMENT_RESEALED`.

Completion time: 2026-08-16T23:49:21+08:00

The committed product now provides AnalysisIntent 1.1's bounded exact
DataProfile-backed material-property targets. It preserves AnalysisIntent 1.0
readability and rejects unknown, ambiguous, stale, foreign-dataset,
non-material-property, duplicate/conflicting, incomplete, and same-axis
scatter targets. No property vocabulary, fuzzy/first-column selection, unit
guessing, scientific Tool/algorithm, ToolPlannerMetadata prerequisite, support
surface, or AnalysisPlan cap changed.

The R1.6 authority uses the real JARVIS material-property table and four
natural Q-TABLE turns for `table.numeric_summary`, `viz.histogram`,
`viz.correlation`, and `viz.scatter`. The independent content-and-contract
preflight passes all 16 Cases and 26 declared analysis turns, with one valid
expected pre-Plan rejection and zero authority conflicts. The package is
`_qualification/inputs/Phase_BC_R1_6_Qualification_Authority_Reconciled.zip`.
Its integrity evidence is package inventory, schema/contract validation,
protected direct content comparison, and direct byte-for-byte double-build
comparison; active qualification checksum/digest gates are not used.

Phase D independently reran the complete preflight and sealed a fresh official
migration namespace at `0008_phase_d_r1_namespace`. PostgreSQL, Redis, MinIO,
backend, fresh Worker, browser app shell, provider configuration, and required
credential presence passed. Browser evidence proves normal-user binary ZIP and
bounded same-dataset multi-resource import/readiness for Archive, XRD, and
Electronic inputs; restart evidence proves Project and persisted object-storage
durability. Formal namespace counts for Intent, Plan, Job, ToolCall, Artifact,
Report, and Recipe are all zero. `REAL_LLM_CALLS=0` and formal qualification
execution remains zero. Phase E was neither created nor started.

Tests: focused backend `159 passed`; focused product regression `124 passed`;
frontend typecheck PASS; frontend Vitest `460/460`; production build PASS with
existing Plotly/glslify warnings; sealed Docker-network durable namespace test
`1 passed`. Full repository pytest is disclosed as `1514 passed, 20 failed,
51 skipped`; failures are 19 obsolete historical queue assertions and one
pre-existing Phase 13 evidence-size mismatch, with no R1.6 product/runtime
regression. Remote CI was not run or claimed.

Evidence: `_qualification/evidence/phase_bc_r1_6/` and
`_qualification/evidence/phase_d/attempt_09_r1_6_reseal/`.

## Phase E-R1.6 — Canonical Live-Agent Browser Qualification Restart

状态：失败 / `PHASE_E / BLOCKED_AUTHORITY_CONFLICT`

完成时间：2026-08-17T02:20:46+08:00

本次任务从新的 R1.6 campaign state 开始并使用真实 Browser、真实 DeepSeek、
真实 Planner、Queue、Worker、Artifact、Workspace/Renderer 和 Report 链路。
Q-TRAJECTORY-001 的真实浏览器上传、资源 Profile 和第一 turn
`structure.trajectory_viewer` 均通过；第二 turn 真实生成了包含
`trajectory.diffusion`、`trajectory.msd`、`trajectory.rdf` 的 3-step
依赖计划，但 Worker 对 `trajectory.msd` 与 `trajectory.rdf` 返回
`TOOL_RESOURCE_LIMIT / TRAJECTORY_TOO_LARGE`，Job 失败。

根因：冻结资源实际为 650 frames、516 atoms，而当前已发布
`trajectory_analytics` Adapter 的正式上限为 200 frames、5000 atoms；冻结
Case 要求完整 supplied time range。未提高上限、未截断/重采样轨迹、未合成
科学数据、未修改 R1.6 package，因此该问题属于冻结 authority 与已发布
科学资源边界冲突，不是可在 Phase E 内无审查修复的普通 runtime bug。

修改文件：
`_qualification/evidence/phase_e_r1_6/discovery_20260817_r1_6_01/cases/Q-TRAJECTORY-001/TRAJECTORY_RUNTIME_CAP_BLOCKER.json`、
`TASKS.md`、`results.md`。历史 evidence 与历史任务未删除或改写。

测试/执行结果：Q-TRAJECTORY 第一 turn 真实 Browser/DeepSeek/Planner/Queue/
Worker/Artifact/Renderer/Report PASS_DISCOVERY；第二 turn真实 Job 失败。
`REAL_LLM_CALLS > 0`，未发生 handcrafted Intent/Plan/Job/ToolCall/Artifact/
Report/Recipe injection。未执行后续 Cases，因此不能声明 16/16，也不能声明
Phase E PASS。Phase E-R1.6 队列任务按硬阻塞规则保留为失败，后续需要新的
有效 fixture 或经 Reviewer 批准的产品/authority 变更。

## Phase B/C-R1.7 — Trajectory Resource-Cap Authority Reconciliation

状态：已完成 / `PHASE_BC_R1_7 = PASS / TRAJECTORY_RESOURCE_CAP_AUTHORITY_RECONCILED_AND_REFROZEN`

完成时间：2026-08-17T08:36:15+08:00

Reviewer 决议已落实为 qualification fixture replacement，而非产品 cap 扩展。
新 Q-TRAJECTORY 使用 Lei et al. Cage-1 500 K 真实 AIMD 源的首个预先定义连续
窗口 frames 0-14：15 frames、516 atoms、0-1050 fs、固定晶胞、PBC 全开、
source-backed unwrapped Cartesian coordinates。所有 atoms/species/order、
coordinates、cell/PBC 与 timestamps 保持；无结果驱动选择、插值、重采样、
atom subset 或运行时截断。

Registry 资源上限元数据已对齐既有 Adapter 强制上限，未改变算法、工具集、
科学支持面或运行时行为。通用 cap-aware preflight 可在正式执行前复现旧
650-frame authority 的 frame cap、RDF pair-evaluation cap 和 wrapping authority
冲突；新 fixture 的 viewer/MSD/diffusion/RDF 资源与依赖预检全部 PASS。

全量结果：16/16 Cases、26/26 analysis turns、expected rejection PASS；
resource-cap conflicts 0，unpreflightable required Tools 0，preflight test errors 0。
15 个非轨迹 Case 的保护内容逐文件字节一致。R1.7 package 为
`_qualification/inputs/Phase_BC_R1_7_Qualification_Authority_Reconciled.zip`，
116 个排序条目、16 个唯一 Case、无缺失/重复，双构建直接字节相等；未生成
checksum/digest/fingerprint qualification manifest。

修改文件：Registry cap metadata、R1.7 authority/preflight scripts、聚焦测试、
R1.7 package/evidence、`TASKS.md`、`results.md`。测试为 `31 passed`；未运行
remote CI。`REAL_LLM_CALLS=0`，正式 qualification executions/Jobs/ToolCalls/
Artifacts 均为 0。产品及预检变更已提交；Phase D R1.7 由独立任务执行。

## Phase D R1.7 — Live Qualification Environment Re-Seal

状态：已完成 / `PHASE_D = PASS / LIVE_QUALIFICATION_ENVIRONMENT_RESEALED`

完成时间：2026-08-17T09:06:46+08:00

Phase D 针对当前稳定 committed product state 与独立 R1.7 authority 从头执行。
fresh PostgreSQL database 已通过正式 migration 到
`0008_phase_d_r1_namespace`；Redis、MinIO、API、frontend 和 fresh Worker 均
健康。Provider 配置可解析且所需 credential 存在，但没有发起真实 LLM 调用。

独立 cap-aware preflight 再次得到 16/16 Cases、26/26 analysis turns PASS，
resource-cap conflicts 和 unpreflightable required Tools 均为 0。Browser 使用
正常上传入口导入新 Q-TRAJECTORY fixture，实际 Profile 为 15 frames、516 atoms、
0-1.05 ps、Cartesian/unwrapped、fixed cell、PBC 全开，trajectory resource-cap
readiness PASS。fresh namespace 中 AnalysisIntents、AnalysisPlans、Jobs、
ToolCalls、Artifacts、Reports 和 Recipes 均为 0。

测试结果：聚焦回归 `31 passed`；current runtime/qualification 回归
`212 passed`；frontend Vitest `460/460`、typecheck/build PASS；service-backed
trajectory integration `1 passed`。完整 pytest 为
`1534 passed, 20 failed, 51 skipped`；20 项是既有历史 queue/evidence 断言，
不涉及当前 R1.7 runtime path，因此不声明仓库全量 CI PASS。remote CI 未运行。

证据位于 `_qualification/evidence/phase_d/attempt_10_r1_7_reseal/`。
`READY_FOR_PHASE_E=YES`，但本任务没有创建或启动 Phase E。

---

任务：Account → Project Authorization Contract Closure（2026-08-20）
状态：已完成
完成时间：2026-08-20
修改文件：`apps/api/mdi_api/access.py`（复用既有统一边界）、`apps/api/mdi_api/routers/project_history.py`、`apps/api/mdi_api/routers/secured_runtime.py`、`apps/api/mdi_api/phase1_demo.py`、`apps/api/mdi_api/main.py`、`apps/api/mdi_api/routers/secured_planner.py`、`tests/test_project_access.py`、`persistent/ARCHITECTURE_DECISIONS.md`
修改摘要：项目历史在同步前授权；旧 Phase 1 事件流、Demo 数据和解释 Evidence 均继承 Project 授权；项目列表按 owner/member 返回且不泄露私有项目；补充 viewer 写拒绝、跨用户列表过滤和过期会话拒绝测试。未修改 CI、迁移或历史数据。
测试结果：授权/历史/Planner/legacy demo 相关测试 `23 passed`；新增授权测试 `4 passed`；无失败。
提交/CI：未提交；CI 未修改。

补充：新版 Console 增加可发现的项目搜索入口；受保护深链首次未登录时保留安全的
同源 `returnTo`；历史 `/analysis` 与 `/workspaces` 先完成服务端授权解析，再跳转
新版 Project Research；无法解析时只给非泄露兼容状态。`npm run typecheck` PASS；
`npm run test -- --run app/components/ProductPages.test.tsx` = 3 passed；未修改 CI、
迁移或数据。

任务名称：Phase E-R1.7 — Canonical Live-Agent Browser Qualification Restart
状态：已完成
完成时间：2026-08-17T15:55:43+08:00
最终候选：`d7c267f9d5cac1397cbe56368e8de94f0b9d69e3`

修改摘要：完成 durable ProjectHistoryView/1.0、项目历史首页、独立 Dataset
Workbench 与 Planner 恢复导航；修复电子 Band+DOS 显式工具对和 provider stale
resolution 未进入单次 repair budget 的缺陷。最终 candidate9 使用独立 PostgreSQL
database、Redis、fresh API/Worker 和 frontend，Phase D attempt23 通过。随后在
`final_20260817_03` 中从 Case 1 开始完成同一 SHA 下 16/16 Cases、26/26 turns，
真实 DeepSeek、Queue/Worker、36 ToolCalls、151 Artifacts、26 Workspaces、26
grounded Interpretations、26 Report Preview/Finalize、26 Recipes 全部验证通过，
Recipe executed=0，unexpected fallback/injection/fatal error=0。

测试结果：capability planner `57 passed`；Project History `1 passed`；frontend
focused `36 passed`；typecheck PASS；production build PASS；compileall PASS；Phase D
R1.7 attempt23 PASS；final campaign 16/16 PASS。最终 evidence 共 471 files，其中
359 JSON 全部可解析，secret scan 0 命中，`git diff --check` PASS。remote CI 未运行，
未执行 push/deploy。

证据：`_qualification/evidence/phase_d/attempt_23_r1_7_candidate9_reseal/` 与
`_qualification/evidence/phase_e_r1_7/final_20260817_03/`。

---

任务名称：Release Closure — Full Repository Green + Push + Remote CI
状态：已完成 / `PASS / FULL_REPOSITORY_GREEN_AND_REMOTE_CI_VERIFIED`
完成时间：2026-08-17T19:42:17+08:00

Phase E-R1.7 canonical qualification 保持
`PASS / R1_7_CANONICAL_LIVE_AGENT_BROWSER_QUALIFICATION_COMPLETE`，未重开、
未重跑或改写 16-Case/26-turn authority 与 evidence。Release Closure 独立完成
仓库测试债清理：初始本地 21 项和 clean-checkout 追加暴露的 7 项均为过时历史
queue/evidence/docs assertions；共 28 项改为当前 queue invariant、内容级 evidence
inventory/JSON/semantic validation 或受支持入口断言。真实当前产品缺陷 0，
qualification-relevant regression 0。

本地验证：backend `1563 passed, 0 failed, 0 errors, 53 deselected, 75 warnings`；
service-backed PostgreSQL/Redis/MinIO/migration `50 passed, 0 failed, 0 errors,
0 skipped`；frontend Vitest `465 passed`，TypeScript typecheck 和 production build
PASS。Chromium/Firefox/WebKit、390x844 及当前全部 browser/replay gates PASS，
包括 Phase 10M-4 Artifact Gallery headful CI replay。compile、lock、diff、schema、
queue、secret 和 private-path checks PASS；`REAL_LLM_CALLS=0`。

提交/CI：Release Closure changes 正常提交并 push 到 `origin/master`；GitHub
Actions run `32024851926` 的 Unit、Linux/Windows semantic replay、Frontend
Typecheck & Build、PostgreSQL/Redis/MinIO service-backed integration 全部 PASS。
production runtime-affecting release-owned uncommitted diffs 为 0；已分类的本地
历史 qualification/evidence 与用户工作区改动保持未提交且未改写。

部署：`NOT_STARTED`。`READY_FOR_DEPLOYMENT_REVIEW=YES`，开放 Release blockers 0。

---

任务名称：UX-V1.3 — Design Documentation + High-Fidelity Prototype
状态：已完成
完成时间：2026-08-18T01:11:04+08:00

修改摘要：在 `design/ux-v1.3/` 创建正式 UX-V1.3 设计资产、Chrome reference
research、Design Reality Matrix、状态/响应式/可访问性规范和隔离高保真原型；
在 `.interface-design/system.md` 建立长期 Scientific Research Workbench 视觉系统。
Prototype 覆盖 Landing、Console、Projects、Project Overview、Project Data 的
Table/Structure/Trajectory/XRD/Electronic/Volumetric/Archive/Unsupported 状态、
Research 的九种状态、增量结果、Inspector、Quick Preview、Reports 与 Report Reader。

修改文件：`.interface-design/system.md`、`design/ux-v1.3/**`、
`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、`TASKS.md`、
`results.md`。

测试结果：`node --check design/ux-v1.3/prototype/prototype.js` PASS；Chrome
实际审阅 1920x1080、1440x900、1280x800 和约 391x844 CSS viewport；关键 Research
states、Data/Inspector、Quick Preview、Escape/focus restoration、图标 accessible
name、字体加载和默认内部术语泄漏检查 PASS。`git diff --check` PASS。移动截图通道
出现工具层拼贴异常，已通过 Chrome DOM 尺寸、滚动/overflow 和 Inspector geometry
复核并记录为验证限制；未运行 production build/test，因为本任务未改生产代码。

提交/CI：未提交、未推送、未运行 remote CI；本任务是设计资产和隔离 prototype，
不触发 release/deploy 生命周期。部署：NOT_STARTED。

---

任务名称：Current Product Acceptance — 16-Case Chrome UI Verification
状态：已完成（16/16 最终补测通过，原始失败记录保留）
完成时间：2026-08-18

使用本机 Google Chrome 真实执行上传、项目创建、研究问题提交、等待分析、截图和
结果采集。两次完整 16-case 运行分别保留在
`_qualification/evidence/current_product_acceptance_16_cases/run_2026-08-18T14-18-48-070Z/`
和 `run_2026-08-18T14-32-02-801Z/`；首轮与第二轮的失败均未删除。随后对
Q-ATOMIC-VIEW-001、Q-ML-REG-001、Q-PHONON-001、Q-COMPOSITION-001、
Q-COORD-001、Q-TRAJECTORY-001 逐案进行新增 Chrome 补测，最终均为
`PASS_OR_RECORDED`，索引见
`_qualification/evidence/current_product_acceptance_16_cases/FINAL_RECONCILIATION.json`。

修改摘要：验收 runner 将 `INTENT_UNSUPPORTED` 纳入合法预期拒绝；上传页面根据
声子 band/DOS 文件名绑定 typed phonon companion import 与 schema contract，修复
Q-PHONON 在真实 UI 上传链中的 bundle 解析失败；补充对应前端回归测试。未删除任何
项目、Dataset、Conversation、Job、ToolCall、Artifact、Report 或历史 qualification
evidence，Phase E-R1.7 未重开。

测试结果：完整 Python `1576 passed, 51 skipped, 0 failed`；frontend Vitest
`475 passed`；TypeScript typecheck PASS；production build PASS（仅既有 Plotly/
glslify critical-dependency warning）；`python -m compileall -q apps/api/mdi_api`
PASS；`git diff --check` PASS。API 持久化核验确认本次项目、Dataset、analysis、Job、
ToolCall 和 Artifact 仍可读取。部署：NOT_STARTED；CI：未修改。
---

任务：Production UI/UX Reconstruction — Full Production Completion（2026-08-19 研究结果闭环续作）
状态：处理中（核心产品验收仍有明确债务）
完成时间：2026-08-19
修改摘要：修复 correlation heatmap 的结构化 Evidence 投影；真实 Q-TABLE Research 运行已完成并保留失败/成功轮次、助手前后消息、Job、ToolCall、Artifact、Interpretation 与结果引用；结果标题和主要发现不再暴露内部 correlation subject 或 raw machine wording；记录 API 重启时必须使用 `uv run ... --app-dir apps/api`，避免 `mdi_adapters` 导入失败造成误报 500。补充 bounded numeric trajectory scan、source viewer 与持久化投影相关验证记录。
测试结果：`pytest tests/ -q` = 1584 passed, 51 skipped, 75 warnings；`npm run test -- --run` = 79 files / 494 tests passed；`npm run typecheck` PASS；独立输出目录 `MDI_NEXT_DIST_DIR=.next-acceptance npm run build` PASS，仅保留既有 Plotly/glslify critical-dependency warnings；`python -m compileall -q apps/api packages services tests` PASS；`git diff --check` 无 whitespace error。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — 46-project scientific presentation batch
状态：已完成（保留明确验收债务）
完成时间：2026-08-20
修改摘要：使用生产 Chrome 路由和已配置服务端 Provider 批量复核 39 个保留科学
Project 的 Data、Research、Result、Evidence 与 Report 展示；统一 Project 命名为
`Case NN · Q-ID · Run NN`；对 35 个过时终态 Run 使用可逆 project-scoped archive，
Reports 默认只显示最新高可用 Run。四个原始空 Project 与三个测试产生的零子对象
Project 在 SQLite 备份后物理删除；没有删除任何科学数据链或历史 qualification evidence。
新增/更新批量 Chrome 证据位于
`design/ux-v1.3/evidence/production/batch-20260820/`。
测试结果：42 Projects / 39 Datasets / 109 Jobs / 615 Artifacts / 208 Messages /
42 Interpretations；Python `1603 passed, 51 skipped`；Vitest `79 files / 511 tests`；
`npm run typecheck` PASS；production build PASS；`python -m compileall -q apps/api services packages tests`
PASS；`git diff --check` PASS。增量非终态结果 Chrome 观测为 NOT_OBSERVED，真实读屏设备
为 NOT_VERIFIED，BZ source ingestion 与 BYOK 为明确非本轮范围。提交/CI：未提交；
CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — Project 命名与 Phase 10 能力可发现性修正
状态：已完成
完成时间：2026-08-20
修改摘要：依据批处理前 46-Project 备份重新判定 provenance；38 个 Q-ID 科学项目
统一为 `Case NN · Q-ID · Run NN`，3 个历史会话与 1 个历史数据项目使用
`其他 · ... · Run NN`。未把 Case 项目错误伪装为 Phase 项目。为所有 Case 增加中文
科学能力说明和真实 Phase 10 能力来源；Projects 页面新增 Case/Phase/其他分组、自然
数值排序及按名称、Q-ID、Phase、能力说明搜索。数据库改名前备份为
`mdi_phase5.db.pre-phase10-discoverability-20260820.sqlite`，未修改或删除 Dataset、Job、
Artifact、Message、Evidence、Interpretation 或 Report。
测试结果：ProductPages Vitest `5 passed`；TypeScript typecheck PASS；focused
`git diff --check` PASS；Chrome `/projects` 实际显示 42 个项目，搜索 `Phase 10H`
仅返回 Q-PHONON 的 Run 01/02，中文能力说明和 Phase 10H/10I 来源可见。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — Remaining debt classification（2026-08-20）
状态：已完成（无可自行消解的产品债务）
完成时间：2026-08-20
修改摘要：补充语义可访问性审计证据，标明真实硬件读屏与浏览器非终态 Artifact 截图的工具/执行时序限制，并将旧 Chrome 网络和 Volumetric 说明标为历史。`next lint` 已实际尝试，因缺少 ESLint 配置而进入 Next 弃用的交互式初始化；该项保留为工程卫生债务，不通过修改脚本伪造 PASS。BYOK、多 Dataset Job、ZIP 持久目录和完整 Phase E live campaign 继续按既定范围排除。
测试结果：`npm run lint` = `ENGINEERING_DEBT`（交互式初始化，未产生代码检查结果）；`python -m compileall -q apps/api packages services tests` PASS；此前完整 Python `1599 passed, 51 skipped`、Vitest `79 files / 510 tests`、typecheck/build PASS；`git diff --check` PASS。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — Scientific presentation and Phase 10 closure（2026-08-20）
状态：已完成（核心生产闭环已实现；明确验收债务保留）
完成时间：2026-08-20
修改摘要：完成共享 Scientific Viewer adapter/registry 的源数据与结果投影收拢；修复声子组合结果优先级与重复输出、通用科学曲线的极值保真抽样、轨迹/布里渊区/材料模型/电子结构用户文案；Research roles、Project authorization、Evidence/Report projection 继续沿用服务端事实与现有执行内核。新增当前生产 Chrome 证据至 `design/ux-v1.3/evidence/production/desktop/`，未删除历史 qualification 数据、项目、Dataset、Conversation、Job、ToolCall、Artifact、Report 或历史 evidence。
测试结果：完整 Python `1592 passed, 51 skipped, 90 warnings`；Vitest `79 files / 503 tests passed`；授权/Research/Provider/Interpretation/Report 聚焦集 `142 passed`；`npm run typecheck` PASS；production build PASS（仅既有 Plotly/glslify critical-dependency warnings）；`python -m compileall -q apps/api packages services tests` PASS；`git diff --check` PASS。Chrome 复核 Table/Inspector、Trajectory、Electronic、Volumetric summary、Phonon result、Report Reader、Model Settings modal 均无横向溢出；截图桥接可用并已保存桌面证据。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。仍保留真实边界：增量结果在非终态前的 Chrome 观测为 `NOT_OBSERVED`；Volumetric source 3D 与 BZ source ingestion 为 `NOT_SUPPORTED`；真实读屏设备未验证；完整 Phase E live 16-case 不重开。

---

任务：Production UX Correction — Structure Viewer language closure（2026-08-20）
状态：已完成
完成时间：2026-08-20
修改摘要：将三维结构查看器的工具栏、键盘辅助说明、超晶胞、裁剪、相机、导出、测量、位点/键合检查器和可访问语义摘要统一为 zh-CN；保留公式、Å、schema、诊断码等 canonical scientific content。Chrome 刷新验证真实 WebGL canvas、无横向溢出、无主要英文 Viewer labels，保存最终结构证据。
测试结果：Structure Viewer focused Vitest `25 passed`；前端 typecheck PASS；Chrome structure route layout `scrollWidth === clientWidth`，canvas present，English primary-label scan empty；`git diff --check` PASS。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — Semantic accessibility closure（2026-08-20）
状态：已完成（源码/DOM 语义闭环；真实读屏设备仍未验证）
完成时间：2026-08-20
修改摘要：为生产 Research Timeline 增加工作台、对话消息和会话记录语义；补齐搜索弹窗 Tab 循环、Escape 关闭与状态/错误角色；为 Data loading/error/scientific table 增加 status/alert、可访问表名和 caption；研究 splitter 纳入键盘 Tab 顺序并保持 aria-valuenow 边界。新增 Research/Product focused accessibility assertions。
测试结果：`npm test -- --run app/components/ResearchPages.test.tsx app/components/ProductPages.test.tsx` = 2 files / 11 tests passed；`npm run typecheck` PASS；`git diff --check` PASS。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。真实 screen-reader device = NOT_VERIFIED。

---

任务：Production UX Correction — Structure Viewer ordinary-user projection closure（2026-08-20）
状态：已完成（普通用户层级清理；技术详情和高级导出保留）
完成时间：2026-08-20
修改文件：`apps/web/app/components/viewer-scene/ViewerSceneRendererSurface.tsx`、`ViewerExportPanel.tsx`、`ViewerMeasurementPanel.tsx`、`ViewerSceneRendererSurface.test.tsx`、`apps/web/app/globals.css`、`persistent/ARCHITECTURE_DECISIONS.md`
修改摘要：默认隐藏/折叠 renderer/version、图形性能指标、原始 scene/manifest/recipe 下载和导出诊断；新增“高级导出”“技术详情”渐进披露；将 Formula/Species/Lattice、Export size presets、Measurement coordinate mode、导出状态和失败文案统一为 zh-CN；不改变 Three.js、结构数据、校验、导出 contract 或执行内核。
测试结果：viewer-scene 全量 focused Vitest `14 files / 91 tests passed`；单独 `ViewerSceneRendererSurface.test.tsx` `23 passed`；`git diff --check` PASS。`npm run typecheck` 当前被共享工作树中未提交的 `apps/web/app/components/ResearchPages.tsx` 语法错误阻断（该文件非本任务修改，需主任务合并前修复）。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Production UI/UX Reconstruction — Full Production Completion（最终闭合）
状态：已完成
完成时间：2026-08-20
修改摘要：完成账号到 Project 的服务端授权边界、Research Timeline 与持久化助手前后消息、可信运行过程投影、Scientific Interpretation/Result/Report 投影、共享 Scientific Viewer Registry，以及 Table、Structure/Atoms、Trajectory、XRD、Electronic、Phonon、BZ Result、Volumetric、ZIP detected-content 和 Generic fallback 在新版 IA 中的接入。最后修复 Volumetric source channel 的通用列表截断、严格 Phase 10J source projection、attached source payload 加载、125×72×60 Gaussian-cube 等值面/精确切片/直接体渲染、通用标量错误模块投影和中文产品文案。保留历史项目、Dataset、Conversation、Job、ToolCall、Artifact、Report 与 qualification evidence；未重开 Phase E。
测试结果：完整 Python `1599 passed, 51 skipped, 90 warnings`；完整 Vitest `79 files / 510 tests passed`；`npm run typecheck` PASS；`MDI_NEXT_DIST_DIR=.next-acceptance-final-4 npm run build` PASS（仅既有 Plotly/glslify critical-dependency warnings）；`python -m compileall -q apps/api services` PASS；`git diff --check` PASS。Chrome 真实验证保留的 Volumetric 125×72×60 source 可渲染 24,532 顶点/47,242 三角形等值面、精确晶格切片和 WebGL2 直接体渲染；BZ supporting result 真实渲染；390 与 200% 证据保存在 `design/ux-v1.3/evidence/production/`。
验收边界：增量 Artifact 的非终态事件顺序由真实两步 Adapter 自动化验证，因当前本地 Worker 同步完成而没有浏览器中间态截图；真实硬件屏幕阅读器未运行，但源码与 Chrome DOM 语义审计通过；BZ 无 normalized source object，因此 Source View 为 NOT_SUPPORTED、Result View 为 VERIFIED；BYOK、CI modernization、完整 16-case live requalification 均不属于本任务。
LLM 角色闭合：Research Turn Orchestrator 已接入可选真实 Provider，输入边界为问题/数据集/已验证 Plan，严格 JSON 失败时 grounded fallback；Report Composer 已接入 finalize，引用、来源身份和数值事实均经 Scientific Result 校验后才持久化；运行过程仍为零 LLM 调用。
提交/CI：未提交、未推送；CI/GitHub Actions 未修改；未部署。

---

任务：Production UX Correction — Final documentation reconciliation（2026-08-20）
状态：已完成
完成时间：2026-08-20
修改摘要：将 `persistent/TASK_BOARD.md` 的生产重构条目标记为“已完成（明确验收边界）”，并在 `persistent/OPEN_QUESTIONS.md` 中关闭已由当前 Research Turn/Report Composer 严格角色合同取代的旧问题描述。未改变历史 Phase 证据、数据库、CI 或运行时行为。
测试结果：`python -m compileall -q apps/api packages services tests` PASS；Model Settings Vitest `5 passed`；此前最终全量 Python `1599 passed, 51 skipped`、Vitest `79 files / 510 tests`、typecheck/build PASS；`git diff --check` 无 whitespace error。
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。

---

任务：Continuous Product Quality — Global UX / Scientific Capability / Accessibility Improvement Wave 1
状态：已完成
完成时间：2026-08-20T22:52:15+08:00
修改摘要：修复 Data 科学表格的单位猜测问题，改为仅显示未声明单位并使用中文语义标签；为 Research 增加初始加载/错误/重试状态、研究记录弹层焦点恢复与中文会话状态；在移动端加入 Research 对话/工作台单面板切换并降低滚动冲突；将 Reports 列表和 Report Reader 改为显式加载/错误/结果优先层级，并优先 PRIMARY_FIGURE / PRIMARY_TABLE 作为主结果。
测试结果：`npm test -- --run app/components/ResearchPages.test.tsx app/components/ProductPages.test.tsx` = 2 files / 27 tests passed；`npm run typecheck` PASS；`npm ci` in apps/web PASS after removing a locked Next process.
提交/CI：未提交；CI/GitHub Actions 未修改；未部署。Chrome 真实视觉证据待重连用户 Chrome 标签页后补验。

Wave 1 follow-up（2026-08-20）：补齐 validated objectType 优先路由，修复 phonon→electronic 误判；结果加载改为 selected Artifact 必需、伴随 Artifact best-effort；通用表格披露完整行数与 preview cap；未知 source object 使用诚实 unsupported 状态。Focused `ProductPages` + `ScientificViewerAdapter.effect` = 19 passed；typecheck PASS；Chrome 桌面复查 Q-TABLE-001（64 行）和 Q-TRAJECTORY-001 Research 时间线 PASS。390px 视口仍待用户实际调整后验收。
追加回归：完整 `pytest tests/ -q` = 1607 passed, 51 skipped, 90 warnings（239.24s）；完整 Vitest = 80 files / 529 tests passed；无失败。最终 Chrome 390×845 验收 PASS：Research 对话/工作台单面板切换且 viewport scrollWidth=390；Data 页面无 viewport 横溢出，表格使用独立横向滚动；行选择与模型设置关闭按钮均为 44px；Inspector Escape 恢复“选择第 1 行”；Report 列表与 Reader 无 viewport 横溢出。

---

任务：Continuous Product Quality — Research Timeline / Scientific Workbench Wave 2
状态：已完成
完成时间：2026-08-21
修改文件：`apps/api/mdi_api/db.py`、`apps/api/alembic/versions/0014_research_session_run_bindings.py`、`apps/api/mdi_api/routers/research.py`、`apps/api/mdi_api/routers/secured_planner.py`、`apps/api/mdi_api/routers/planner.py`、`apps/api/mdi_api/routers/project_history.py`、`apps/web/app/lib/planner-api.ts`、`apps/web/app/lib/product-api.ts`、`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/components/workspace/WorkspaceGenericPlot.tsx`、`tests/test_project_access.py`、`tests/test_research_session_run_migration.py`、`docs/13_SHARED_SCHEMA_SPEC.md`、`persistent/ARCHITECTURE_DECISIONS.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`。
修改摘要：将 Research Session → Planner Run 关联正规化为项目级、一个 Job 只能归属一个 Session 的可审计投影；迁移从旧 assistant payload 回填且不删除历史记录，旧数据库在迁移窗口保持可读并明确标记 `migration_required`。Planner 请求携带经授权校验的 `researchSessionId`，解释完成后服务端自动补齐 post-run 助手投影；failed 投影有幂等保护。历史 Run 恢复增加部分加载保留、事件/Artifact 合并去重、孤立 Run 不自动挂入首个会话，以及 Data/Report/Research 互链。Provider 与 Session 读取失败均有可重试状态；图表超限提示不再重复出现在无障碍树中。
测试结果：完整 Vitest `80 files / 539 tests passed`；完整 `pytest tests/ -q` `1611 passed, 51 skipped, 90 warnings`；`npm run typecheck` PASS；`MDI_NEXT_DIST_DIR=.next-wave2-build npm run build` PASS（仅既有 Plotly/glslify critical-dependency warnings）；`python -m compileall -q apps/api packages services tests` PASS；Alembic `0014_research_session_run_bindings (head)`；`git diff --check` PASS。针对性新增/更新 Research、授权与迁移回归全部通过。
Chrome 验收：真实保留项目 `Case 11 · Q-STRUCTURE-RDF-001 · Run 02` 在 Chrome 桌面双栏与 390px 单面板下通过；历史结果经异步加载恢复，Data/Report 回链可用，移动 `scrollWidth === clientWidth`。提交/CI：未提交；CI/GitHub Actions 未修改；未部署。已知限制：本地 Worker 同步完成导致非终态 incremental Artifact 未在浏览器中观测；真实硬件 screen-reader 未运行；Plotly 构建警告仍属依赖层既有问题。

Wave 2 follow-up（2026-08-21）：将 Research Turn 的确定性用户文案从“我会使用 …”
调整为“本次分析将以数据集“…”为范围”，并统一 unsupported 文案的数据集边界表达，
并在前端展示层兼容旧的 pre-run 前缀，因此无需重写历史 Message。保留原始科学数据集名称不做翻译或猜测。`tests/test_product_research_scope.py` = 9 passed；
Research/Product Vitest = 37 passed；`npm run typecheck`、compileall、`git diff --check` PASS。

---

任务：Continuous Product Quality — Exact Structure Planning / Evidence / Workbench Closure
状态：已完成
完成时间：2026-08-21T09:47:57+08:00
修改文件：`services/llm/mdi_llm/capability_planner.py`、`services/llm/mdi_llm/providers.py`、`apps/api/mdi_api/routers/planner.py`、`apps/api/mdi_api/routers/research.py`、`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/globals.css`、相关 Python capability/evidence/research tests、`persistent/*.md`。
修改摘要：补齐中文“径向分布+局部环境”的精确识别与 CrystalNN/VoronoiNN 操作型澄清；算法确认后严格生成配位 producer、局部环境 consumer 与 RDF 三步计划，并保留局部环境+实验 XRD 的四工具组合合同。超出 262144-byte 读取上限的已支持 Artifact 改为有界跳过并披露限制，不再阻断其余安全 Evidence；Research/Report 将配位覆盖率、范围和算法限制转成用户可读中文。桌面 Research 改为动态视口固定壳体、左右独立滚动、320-640 px 鼠标/触控/键盘 splitter，进入路由时归零根滚动。
真实验收：使用已授权本地账号在 `http://localhost:3000` 完成 Run `job_07f702a3c9af42259ec5d14f`；Plan 仅含 `structure.coordination_crystalnn`、`structure.local_environment_polyhedra`、`structure.rdf`，完成 4 个科学输出并渲染 5 个 RDF 系列 / 400 个值。1280x720 实测全局栏、项目导航和 620 px 工作台无根滚动，长对话与结果独立滚动；Grounded finding/limitation 恢复成功。
测试结果：完整 `pytest tests -q` = `1618 passed, 51 skipped, 90 warnings`；完整 Vitest = `82 files / 552 tests passed`；Research focused = `24 passed`；修复后的 Phase 13 composite capability/preflight + capability planner = `92 passed`；`npm run typecheck` PASS；`MDI_NEXT_DIST_DIR=.next-continuous-wave3 npm run build` PASS（仅既有 Plotly/glslify critical-dependency warnings）；`python -m compileall -q apps/api packages services tests` PASS；Alembic = `0014_research_session_run_bindings (head)`；`git diff --check` PASS。
提交/CI：未提交、未推送；CI/GitHub Actions 未修改；未部署。真实硬件 screen reader 与浏览器中的非终态 incremental Artifact 仍未验证，本轮未重开 Phase E。

---

任务：Remaining Acceptance Closure + Evidence-Based CI Rationalization + Commit/Push
状态：已完成
完成时间：2026-08-21
修改摘要：基于 workflow、仓库脚本、测试标记、路线文档和远程失败/成功运行记录，区分当前产品门禁与已封存历史证据。默认 Python 单元门禁排除明确标记且依赖忽略目录 `_qualification/` 的 qualification 模块；旧 Phase 13-4 Help 浏览器检查保留为历史证据但移出 push gate；17 个历史 Phase 10/12 浏览器步骤合并为一个手动 dispatch 编排步骤，仍逐项执行并在失败时停止。当前 Phase 12-6/12-7 改为验证项目级 Research 工作台，补齐 skip link、splitter 和确定性只读 fixture。未移除科学重放、跨平台、服务集成、迁移、完整前端、typecheck、build 或当前可访问性/UX 门禁。
测试结果：本地默认 Python `1586 passed, 1 skipped, 82 deselected, 75 warnings`；qualification `30 passed`；Vitest `83 files / 554 tests`；typecheck PASS；production build PASS；Phase 12-6/12-7 Playwright PASS；Phase 12 evidence integrity `10 passed`；focused contract tests `16 passed`；`uv lock --check`、compileall、YAML parse、`git diff --check` PASS。
提交/CI：`501313a`、`ef86945`、`0df1e97` 已推送；current HEAD `0df1e97ee21533e8f9d620d0810cea6129a71bd3` 的 GitHub Actions run `32454012102` 全部通过（Unit Tests、Scientific Replay Linux/Windows、Frontend、Service-backed Integration）。未部署或发布。用户临时/历史未跟踪文件未加入提交。

---

任务：Continuous Product Quality — Research history navigation Wave 3
状态：已完成
完成时间：2026-08-21T16:30:12+08:00
修改文件：`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/globals.css`、`persistent/ARCHITECTURE_DECISIONS.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、`TASKS.md`、`results.md`。
修改摘要：将 Research 记录浮层补全为高频历史导航：本地标题搜索、记录数量、空/无匹配状态、长列表滚动边界、当前记录标识、Escape/外部点击/选择关闭与焦点恢复。移动搜索输入固定为 16px。依据数据库事实将 `sessions.status=active` 从误导性的“进行中”改为“可继续”，并保留 queued/running Planner Job 的“进行中”语义；未改变会话归属、Planner、Artifact、Report 或执行权限。
测试结果：Research focused Vitest `25 passed`；完整 Vitest `83 files / 554 tests passed`；`npm run typecheck` PASS；独立 production build PASS。真实已授权 Structure/RDF 项目在 1280x720 验证搜索自动聚焦、无匹配反馈、外部关闭、`active` 显示“可继续”、面板边界和文档无横向溢出。
提交/CI：实现提交 `ca8a8b4bcab8de4ad6c094c8cd6f9641200a969b` 已推送；current-HEAD GitHub Actions run `32463181783` 全部通过（Unit Tests、Scientific Replay Linux/Windows、Frontend、Service-backed Integration）。未部署或发布；用户未跟踪文件未加入提交。

---

任务：Continuous Product Quality — Mobile Research navigation Wave 4
状态：已完成
完成时间：2026-08-21T16:52:00+08:00
修改文件：`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/test/phase12-6-responsive-accessibility-browser-evidence.mjs`、Phase 12-6 当前浏览器证据矩阵/截图、`persistent/ARCHITECTURE_DECISIONS.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、`TASKS.md`、`results.md`。
修改摘要：完善移动 Research 的单面板交互：对话/工作台现在使用完整 tab/tabpanel 关联、roving tabindex、Arrow/Home/End 键盘导航和焦点迁移；服务端返回已验证 Planner Job 后自动切换到工作台，让用户立即看到真实运行过程和增量结果。桌面双栏、权限、Planner、Artifact 和 Report 执行边界不变。
测试结果：Research focused Vitest `25 passed`；完整 Vitest `83 files / 554 tests passed`；typecheck PASS；独立 production build PASS；Phase 12-6 浏览器证据 Chromium/Firefox/WebKit PASS，Chromium 390x844 的 tabNavigation、singlePanelVisibility、touchTargets、reducedMotion 和无横向溢出全部 PASS；证据完整性 `5 passed`。
提交/CI：实现提交 `3dccce8a71c5dbfe68a12c0a63af76f5b96a5a38` 已推送；current-HEAD GitHub Actions run `32464949831` 全部通过（Unit Tests、Scientific Replay Linux/Windows、Frontend、Service-backed Integration）。未部署或发布；用户未跟踪文件未加入提交。

---

任务：Continuous Product Quality — Global navigation and structured details Wave 5
状态：已完成
完成时间：2026-08-21
修改文件：`apps/web/app/components/ProductShell.tsx`、`apps/web/app/components/ProductShell.test.tsx`、`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/components/workspace/WorkspaceArtifactGallery.tsx`、`apps/web/app/components/workspace/ScientificWorkspaceShell.test.tsx`、`apps/web/app/globals.css`、`apps/web/test/phase12-7-cross-product-browser-evidence.mjs`、Phase 12-7 当前浏览器证据、`persistent/*.md`、`TASKS.md`。
修改摘要：项目内 Data、Research、Report 路由持续显示全局搜索、模型设置和账户入口；账户操作收拢为支持 Escape、外部点击、Tab、Arrow/Home/End 与焦点恢复的菜单，并验证 390px 无横向溢出。Workspace/科学图表技术详情改为有界 JSON 预览，提供对象/数组摘要、截断提示和空/不可用状态。Research 结果页技术详情显示运行/方案身份、可查看输出数与 JSON Artifact 可用性，不加载或暴露密钥、BYOK 或可执行内容。历史科学、服务集成、迁移与当前 UX 门禁保持不变。
测试结果：针对性 Vitest `54 passed`；完整 Vitest `84 files / 559 tests passed`；`npm run typecheck` PASS；独立 production build PASS（仅既有 Plotly/glslify warnings）；Phase 12-7 Chromium/Firefox/WebKit、1280x720 与 390x844 PASS；Phase 12-7 evidence integrity `5 passed`；`git diff --check` PASS。
提交/CI：实现提交 `e0b84e5` 已推送；current-HEAD GitHub Actions run `32473415268` 全部通过（Unit Tests、Frontend Typecheck & Build、Service-backed Integration、Scientific Replay Linux/Windows）。未部署或发布；用户未跟踪文件未加入提交。

---

任务：Continuous Product Quality — Research activation and capability-aware guidance Wave 6
状态：已完成
完成时间：2026-08-22T02:41:38+08:00
修改文件：`.interface-design/system.md`、`apps/web/app/components/ResearchPages.tsx`、`apps/web/app/components/ResearchPages.test.tsx`、`apps/web/app/globals.css`、`apps/web/test/phase12-7-cross-product-browser-evidence.mjs`、`docs/phase12/evidence/phase12_7_cross_product_ux_validation/*`、`persistent/ARCHITECTURE_DECISIONS.md`、`persistent/DESIGN_PROGRESS.md`、`persistent/TASK_BOARD.md`、`TASKS.md`、`results.md`。
修改摘要：在空白 Research 对话中增加紧凑首次研究区，从所有数据集的 Project History `datasetType`、`readyCapabilities` 与 `semanticRoles` 构建大小写无关、稳定排序且最多三项的建议。formation-energy/band-gap 关系只在两个精确语义同时存在时出现，能力不足时使用中性概览。建议选择只切回对话、填充并聚焦 Composer，不创建 Session、Message、Plan 或 Job。无数据 owner/editor 获得 Upload 入口，viewer 只见只读说明；右侧工作台仅保留数据与最近研究上下文。未修改后端、schema、Planner、Worker、Tool Registry、Adapter 或 CI 策略。
测试结果：Research focused Vitest `32 passed`；完整 Vitest `84 files / 565 tests passed`；`npm run typecheck` PASS；`npm run build` PASS；Phase 12-7 Chromium/Firefox/WebKit、1280x720、390x844 浏览器验证 PASS；Phase 12-7 evidence integrity `5 passed`；`git diff --check` PASS。`npm run lint` 因现有脚本调用未配置且交互式的 `next lint` 无法独立运行；production build 的 lint/type validity 阶段与远端 Frontend job 均通过。
设计验收：Senior Designer 适用检查项 `43/43`；首次路径、加载/错误/空/只读/历史状态、键盘焦点、44px 触控、移动单面板、reduced-motion 与无横向溢出均有实现或浏览器证据。
提交/CI：实现提交 `1032d10a4e0a9111c02246c95cc55f34d6711370` 与完成记录提交 `c1a5a242cbb8f1293c12bc9a6f48001334ad39fa` 已推送；current-HEAD GitHub Actions runs `32514219078`、`32514730110` 的五个 jobs 全部成功（Unit Tests、Frontend Typecheck & Build、Service-backed Integration、Scientific Replay Linux/Windows）。未部署或发布；`CODEX_HANDOFF.md` 保持未跟踪且未纳入提交。

---

任务：Agent-2.0 Phase 1 — Core Domain Foundation
状态：已完成
完成时间：2026-08-22T18:41:46+08:00
修改文件：`apps/api/alembic/versions/0015_agent2_scientific_objects.py`、`0016_agent2_research_turns.py`、`0017_agent2_scientific_results.py`；`apps/api/mdi_api/agent2_errors.py`、`agent2_repositories.py`、`db.py`、`main.py`、`access.py`、`routers/agent2.py`；`apps/api/mdi_api/scientific_objects/`、`research_agent/`、`scientific_results/`；Agent2 unit/API/migration/domain/service-backed tests；integration Alembic helper及现有 integration fixtures；`.github/workflows/ci.yml`；`docs/agent2/`、共享 schema/index/roadmap 与 persistent 权威记录；`AGENT2_PHASE1_RESULTS.md`。
修改摘要：在实际 Alembic head `0014` 后按顺序加入 Scientific Object、Research Turn 与 Scientific Result Snapshot 三个迁移；实现稳定逻辑对象与不可变版本、精确历史引用、项目隔离、原子版本/Turn sequence 分配、CAS 状态机、不可变上下文快照、独立 Registry skeleton、严格 Pydantic contracts、Result Snapshot persistence、授权 REST/SSE 和只读 Scientific Object API。POST Turn 只持久化现有 USER Message、RECEIVED Turn 与 TURN_RECEIVED event，不调用 LLM/Planner，不创建 AnalysisPlan/Job/ToolCall。现有执行内核、62 Tool、Adapter、Viewer 与前端保持增量兼容。
测试结果：Agent2 focused `21 passed`；SQLite migration upgrade/downgrade/re-upgrade `2 passed`；隔离 PostgreSQL migration/concurrency/receive `1 passed`；完整非 integration Python `1607 passed, 1 skipped, 83 deselected`；完整 Vitest `84 files / 565 passed`；typecheck、独立 production build、compileall、`git diff --check` PASS。Current-HEAD CI service integration `51 passed, 0 skipped, 0 failed, 0 errors`，其余 Unit、Frontend/Phase 12-6/12-7、Linux/Windows scientific replay 全部成功。
提交/CI：实现提交 `1553183be2fb561f2ca5e71c2e3d9be2ed31db30` 和 integration compatibility 修复 `9af205b8b411e87e05cce4a05067f676c87bfb23` 已推送；current-HEAD GitHub Actions run `32567895104` 五个 jobs 全部成功。未部署或发布；`CODEX_HANDOFF.md` 保持未跟踪且未纳入提交。
明确未实施：Phase 2 的 Orchestrator LLM、ResearchTurnDecision、语义引用解析、Capability eligibility/planner、Capability→AnalysisPlan binding、Job attachment、production Result projector、Scientific Interpreter、grounding validator、assistant scientific response、Report Composer、全量 Data backfill 与 Viewer integration。

---

任务：Agent-2.0 Phase 2 — Research Turn Orchestration & Context Resolution
状态：已完成
完成时间：2026-08-22T20:48:08+08:00
修改文件：migration `0018_agent2_orchestration_decisions`；`apps/api/mdi_api/research_agent/context/`、`llm/`、`orchestration/`、`evaluation/`；Agent2 repositories/service/router/config/UoW/registry；Phase 2 unit/API/migration/service-backed tests；CI integration gate；`docs/agent2/`、共享 schema/roadmap/index、persistent 权威记录与 `AGENT2_PHASE2_RESULTS.md`。
修改摘要：实现授权且有界的候选组装、固定引用优先级、确定性歧义澄清、不可变 Context Snapshot/fingerprint、`StructuredLLMClient` 与现有 DeepSeek transport adapter、versioned prompt、单次有界 repair、`ResearchTurnDecision 1.0`、Requirement/constraint/ref/action 决策校验、不可变 decision persistence、无事务 LLM 边界、幂等 Redis `turn_id` 唤醒与 AgentTurnProcessor。ANSWER/CLARIFY 完成对话回合；ANALYZE/CONTINUE_ANALYSIS 停在 READY_TO_PLAN；其余 downstream action 仅安全分类。所有 Phase 2 路径保持 AnalysisPlan/Job/ToolCall delta 为 0，未实现或偷跑 Phase 3 能力规划、Tool binding、执行、Interpreter、Report Composer 或数据 mutation。
测试结果：focused Phase 2/API `36 passed, 4 live-gated skipped`；deterministic C01-C15 `15/15`、canonical/paraphrase `60/60`；真实 DeepSeek canonical `5/5`、eligible canonical/paraphrase `48/48`；SQLite migration round-trip `1 passed`；隔离 PostgreSQL/Redis Phase 1+2 service gates `2 passed`；完整非 integration/qualification Python `1638 passed, 5 skipped, 84 deselected`；完整 Vitest `84 files / 565 tests`；typecheck、隔离 production build、compileall、Alembic head、`uv lock --check` 和 `git diff --check` 通过。
提交/CI：实现提交 `9285e0e035ad90af88cd7d9b729e2073a969648f` 已推送；GitHub Actions run `32573620585` 全部通过：Unit `1638 passed`，Service-backed Integration `52 passed / 0 skipped / 0 failed / 0 errors`，Frontend tests/typecheck/build/Phase 12-6/12-7，Scientific Replay Linux/Windows。闭环记录提交将再次以 current-HEAD CI 核验。未部署或发布；`CODEX_HANDOFF.md` 保持未跟踪且未纳入提交。
明确未实施：Capability Resolver/eligibility、CapabilityPlan、Capability→Tool/AnalysisPlan binding、Job attachment、Execution Supervisor/JobEvent progress、production Result projector、Scientific Interpreter/grounded final response、full research memory、Report Composer、Data Management execution、professional Viewer integration 与全 62-Tool capability mapping。

---

任务：Agent-2.0 Phase 3 — Scientific Capability Resolution & Planning
状态：已完成
完成时间：2026-08-22T23:04:38+08:00
修改文件：migration `0019_agent2_capability_planning`；`apps/api/mdi_api/research_agent/capabilities/`、`planning/`；Agent2 errors/repositories/schema/service/router/state machine/orchestration worker；Phase 3 deterministic、migration 与 service-backed tests；CI integration gate；`docs/agent2/`、共享 schema/roadmap/index、persistent 权威记录与 `AGENT2_PHASE3_RESULTS.md`。
修改摘要：实现 `PLAN_READY` 的 pre-Job 状态边界、不可变 CapabilityResolution/CapabilityPlan、九个 manifest 覆盖五类 canonical 科学能力、注册式 deterministic preconditions、精确版本 eligibility、稳定 registry fingerprint、唯一策略 fast path、受限 StructuredLLM planner 与一次 repair、opaque capability/source/result refs、严格 requirement/DAG/port/cardinality/constraint validation，以及 Capability→Tool→现有 AnalysisPlan 0.2 的确定性绑定和 PlanValidator 复核。历史 Result 仅在投影出已授权 exact-version ScientificObject output 时复用；artifact-only legacy Result fail closed。所有成功路径只新增 AnalysisPlan，保持 Job/ToolCall/Artifact/Worker execution delta 为 0。
测试结果：Phase 3 deterministic `19 passed, 1 deselected`，P3-C01 至 P3-C20 全覆盖；live DeepSeek `1 passed`；combined Agent2 `69 passed, 5 deselected`；完整 backend `1657 passed, 1 skipped, 90 deselected`；隔离 PostgreSQL/Redis service-backed Agent2 Phase 1/2/3 `3 passed`；frontend Vitest `84 files / 565 passed`；typecheck、隔离 production build、compileall、Alembic `0019` head、SQLite migration round-trip、`uv lock --check` 与 `git diff --check` 通过。现有 `npm run lint` 仍调用交互式、已弃用的 `next lint`，因此未虚报独立 lint PASS。
提交/CI：实现提交 `855fe3f46298882971227bda684f2529a5823469` 已推送；current-HEAD GitHub Actions run `32580235322` 的 Unit Tests、Service-backed Integration、Frontend Typecheck & Build（含 Phase 12-6/12-7）和 Linux/Windows Scientific Replay 五个 jobs 全部成功。未部署或发布；`CODEX_HANDOFF.md`、`docs/agent2.zip` 与无关 Phase 12 evidence 修改未纳入提交。
明确未实施：Job creation/attachment、queue execution、Execution Supervisor、`PLAN_READY → QUEUED`、Job/ToolCall progress、incremental/production ScientificResult projection、Scientific Interpreter/final scientific answer、long-session semantic memory、Report Composer、Data Management execution、professional Viewer integration、全 62-Tool Agent2 mapping 与 Tool Pack/plugin ecosystem。
---RESULT---
任务名称：Agent-2.0 Phase 4 — Execution Integration & Scientific Progress Projection
状态：已完成
完成时间：2026-08-23T03:09:53+08:00

修改摘要：从持久化 `PLAN_READY` ResearchTurn 接入既有 Job、QueueWorkerRuntime、
ToolCall、Artifact 与 JobEvent 执行内核；新增 `CANCELING`、`RESULT_PENDING`、
不可变 ExecutionSummary、确定性 capability-level 进度、增量 Artifact 输出、
取消竞态收敛、授权 API/SSE 和紧凑响应式 Research activity。Worker 仅凭
`job_id` 从 PostgreSQL/MinIO 恢复 exact-version 输入；执行阶段 LLM 调用为 0，
成功/部分成功均停在 `RESULT_PENDING`，不提前创建 ScientificResult 或助手最终回答。

测试结果：focused Phase 4/API/exact-source `21 passed`；Phase 2 context/processor
回归 `27 passed`；完整非 integration backend `1671 passed, 6 skipped,
86 deselected`；fresh PostgreSQL/Redis/MinIO selection `54 passed,
14 deselected` 且 selected skip 为 0；frontend `85 files, 568 passed`；
typecheck、production build、compileall、`uv lock --check`、科学重放、
Alembic head、浏览器 1440x900/390x844 与 `git diff --check` 均通过。
真实两步 XRD fresh Worker 在 Job 非终态时已观测 step 1 Artifact 和增量输出。
`npm run lint` 仍调用废弃的交互式 `next lint`，未声明独立 lint 通过。

提交/CI：实现提交 `4384db3ae0e92bdd604b8486b738f400eb8b4a97` 已推送；
current-HEAD GitHub Actions run `32592517424` 的 Unit、service-backed integration、
Frontend Typecheck & Build、Linux/Windows scientific replay 五个 job 全部成功。
---END---
---RESULT---
任务名称：Agent-2.0 Phase 5 — Production Scientific Result Projection
状态：失败（实现报告判定 PARTIAL）
完成时间：2026-08-23T10:02:00+08:00

修改摘要：新增 `0021_agent2_scientific_result_projection` 和 `RESULT_READY`；
复用既有 immutable `scientific_result_snapshots`；生产化 typed
ScientificResultBundle、九个 canonical result-projector 注册、稳定 source
fingerprint、exact-version relevance、授权结果 API 与最小 RESULT_READY UI。
所有数值事实需要 committed Artifact locator，image-only Artifact 不产生数值；
Artifact 读取在 DB transaction 外，多能力输入按 step/ToolCall/Artifact lineage
隔离。projection 阶段 LLM/Job/ToolCall/assistant final delta 均为 0。

测试结果：Phase 5 deterministic `5 passed`；focused Agent2 closure `55 passed,
1 skipped`；Alembic migration `1 passed`；完整 non-integration backend `1706
passed, 6 skipped, 56 deselected`；frontend `85 files / 569 passed`；typecheck、
compileall、diff-check 通过。current-HEAD CI run `32611474526` 的 Unit、
PostgreSQL/Redis/MinIO integration（无 skip）、Frontend build/typecheck 与
Linux/Windows scientific replay五个 jobs 全部成功。

未闭合：缺少 Phase 5 专属 fresh service-backed RDF/XRD projection worker
qualification、390px browser result-state evidence，以及按每个 production
Artifact contract 完整定义的领域 metric/figure/table projector 映射，因此未将
`AGENT2_PHASE5` 标记 COMPLETE。实现提交 `5cfe6ae55fa9f3f23277495f7b8b12e49c74e4d9`
已推送；未部署或发布。
---END---
