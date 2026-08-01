# DESIGN_PROGRESS

## 2026-08-01 Phase 10M-1 Implementation In Progress

- Implemented the sealed Workspace domain contracts across Python, checked-in
  JSON Schema, and TypeScript, including strict identity, caps, selection, and
  inert-content validation.
- Added Alembic `0007_phase10m1_workspace_domain`, in-memory/SQLAlchemy
  repositories, explicit historical Job projection, optimistic layout
  revisions, and additive Workspace metadata APIs.
- Focused M1 tests pass, including fresh SQLite migration and constant-query
  project listing. PostgreSQL/Redis/MinIO, browser regression, full suites,
  exact-SHA CI, completion record, and queue archive remain open.
- Workspace UI, panel renderers, selection propagation, and M2 behavior remain
  explicitly deferred.

## 2026-08-01 Phase 10M-0 Audit and IA Seal Complete / Reviewer Approval Required

- Direct reviewer authorization admitted a documentation-only Workspace audit
  without changing `TASKS.md`; task-block count remains zero.
- Current product maturity is `WORKSPACE_LIKE_SINGLE_PAGE`: PlannerWorkbench
  presents the complete chain but has no Workspace entity, route, history,
  aggregate API, saved layout, or global exact selection context.
- M-D001 through M-D025 seal a first-class one-per-Job Workspace, migration
  `0007`, additive APIs, `/workspaces/{workspaceId}`, strict Panel/Selection
  contracts, historical lazy projection, and M1-M7 ordering for reviewer approval.
- Production source, dependencies, lockfiles, current scientific contracts,
  Runtime, Registry, and `TASKS.md` remain unchanged. Audit/planning commit
  `4c5d25e` passed exact-SHA CI run `30698489359`; the separate completion
  record is accepted only after its own exact-SHA CI and is identified in the
  final reviewer return.

## 2026-08-01 Phase 10L Complete / Ready With Explicit Limits

- Phase 10L-4 verified queue archive `58ee943` passed exact-SHA CI run
  `30608078520`: Unit, Frontend/browser/build, and PostgreSQL/Redis/MinIO
  service-backed/no-skipped jobs all succeeded. L4 is
  `ARCHIVED_BY_VERIFIED_QUEUE_COMMIT`.
- Reviewer-approved Phase 10L-5 is the sole active TASKS block. Entry audit
  confirms the canonical Profile -> Intent -> Eligibility -> Plan -> Runtime ->
  Artifact -> Interpretation chain and five required current capability
  families are available. The controlled process uses `DEEPSEEK_KEY` only.
- L5 is implementing a DeepSeek-only real-provider boundary, five genuine
  natural-language closure cases, provider/browser/security evidence, and the
  final Phase 10L lifecycle. Phase 10M-0 remains reviewer-gated.

### Live verification update

- All five frozen natural-language cases passed the real DeepSeek gate.
- Per-case real calls were `3, 3, 3, 4, 3`; total `16`; other real providers
  `0`.
- Each case completed exact Profile -> Intent -> eligibility -> plan -> Job ->
  QueueWorkerRuntime -> artifacts/lineage -> grounded interpretation.
- Dataset and phonon failures from earlier live attempts remain sanitized under
  the evidence directory as regression provenance; they were fixed by strict
  intent disambiguation and exact dependency proposal schema/template context.
- Browser evidence is capture-backed and separately proves the five-case
  UI/API replay across Chromium, Firefox, WebKit, and 390x844 mobile.
- The expanded historical audit is also complete: 40 supplemental semantic
  browser/Mock-LLM cases passed with 92 real DeepSeek calls, for 45/45 total
  current-plus-historical cases. Exclusions are documented by reason and are
  not counted as live LLM coverage.
- Implementation `bfc43bd39d7cc2fa319b9e88f9a4d37eec57ee37` passed
  exact-SHA CI run `30693848581`: Unit Tests, Frontend typecheck/build/browser
  replay, and PostgreSQL/Redis/MinIO service-backed `36 passed, 0 skipped,
  0 failed`. Completion record `e4b0a8f5619cbb1001ef64809db6400729a99d8d`
  passed exact-SHA CI run `30694747664`. The verified queue-archive commit
  removes the completed task; Phase 10M-0 remains reviewer-gated.

## 2026-07-31 Phase 10L-4 Grounded Interpretation Complete, Awaiting Archive

- Corrected implementation `02a9e33b93f96aa99413dc49ca2dabca652679c9`
  passed exact-SHA CI run `30606774006`: unit `955 passed, 1 skipped,
  32 deselected`, service-backed `31 passed, 0 skipped, 0 failed`, and
  Frontend typecheck/build plus committed Chromium/Firefox/WebKit/mobile replay.
- The ML projector now validates the real six-field `ml.basic_metrics` payload
  (`n`, MAE, RMSE, R2, mean error, max absolute error) and a non-service real
  Adapter/Runtime regression prevents fixture-only drift.
- Two failed CI runs remain in provenance: `3336d9f` / `30604842478` exposed a
  missing service fixture import and honest phonon limited outcome;
  `0d37ea9` / `30605450973` exposed the real ML payload mismatch and a test-only
  unsupported-count assertion. Both root causes are corrected without history
  rewrite.
- Completion record `45af09e` passed exact-SHA CI run `30607509775`, including
  all required Unit, Frontend/browser/build, PostgreSQL/Redis/MinIO, and
  no-skipped jobs. L4 is `COMPLETE / AWAITING_ARCHIVE_CI`; L5 remains
  reviewer-supplied and blocked until the verified L4 queue archive.

## 2026-07-30 Phase 10L-4 Grounded Interpretation Implementation Candidate

- Added strict ScientificEvidenceBundle/Item/Ref, ScientificClaim,
  GroundedScientificInterpretation, and InterpretationExecutionRecord 1.0
  contracts across Python, checked-in JSON Schema, and TypeScript.
- Added deterministic, contract-specific projection for dataset/property, ML,
  structure, phonon, and volumetric Artifacts. The real L3
  `phonon.band + phonon.dos -> phonon.band_dos` chain is included; raw Artifact
  text, filenames, paths, URLs, `summary.md`, and failed/blocked outputs are not
  scientific authority.
- Added deterministic and strict OpenAI-compatible interpretation modes, one
  interpretation-only repair, provider-safe evidence isolation, and independent
  numeric/unit/entity/forbidden-conclusion grounding. Default evidence uses
  `REAL_LLM_CALLS = 0` and has no deterministic fallback after provider failure.
- Added Alembic 0006 immutable bundle/run/claim/evidence-link persistence,
  additive interpretation API routes, and an accessible responsive
  PlannerWorkbench findings/evidence surface. Interpretation cannot mutate or
  create Intent, Plan, Job, ToolCall, queue work, Artifact, or Runtime state.
- Focused backend/frontend, evidence integrity, Chromium/Firefox/WebKit, and
  390x844 mobile checks pass locally. Full regression and implementation,
  completion-record, and archive exact-SHA CI remain required before L4 can be
  complete. Reviewer-supplied L5 remains queued and blocked by the L4 archive.

## 2026-07-30 Phase 10L-3 Bounded Dependency Execution Complete and Archived

- Added strict additive AnalysisPlan 0.2 with one authoritative typed
  `dependencyBindings` representation, deterministic binding/graph/plan
  identities, and hard caps of four steps, six bindings, depth four, and three
  incoming/outgoing bindings. AnalysisPlan 0.1 remains unchanged.
- Audited all 38 available tools and admitted only the existing typed phonon
  chain: `phonon.band` and `phonon.dos` produce canonical artifacts consumed by
  `phonon.band_dos`. ToolPlannerMetadata 1.0 remains valid; explicit 1.1 ports
  alone grant dependency composition eligibility.
- Added exact compatible-pair composition, one shared L2/L3 repair budget,
  dependency validation, Alembic 0005 persistence, serial topological
  QueueWorkerRuntime execution, platform-created resolved artifact refs,
  immutable binding/execution/lineage records, and minimal partial semantics.
- Added additive API and PlannerWorkbench dependency/lineage surfaces. Real
  registered-adapter runtime captures and Chromium/Firefox/WebKit/390x844
  browser evidence pass with zero unapproved network and inert artifact
  content.
- Implementation `d395db2a4f59e2f5fb72e0b33b45161b2bcb5670` passed exact-SHA
  CI run `30542148803`: Unit, Frontend, PostgreSQL/Redis/MinIO migration and
  integration, evidence integrity, and no-skipped all succeeded. The local
  service environment remains honestly `UNAVAILABLE`.
- Completion record `2bd06f22562a9fb1baf65730d30682c1d0ca6c54` passed
  exact-SHA CI run `30542844246`, including Unit, Frontend, service-backed,
  migration, and no-skipped. The completed L3 TASKS block is archived by the
  verified queue commit; Phase 10L-4 remains `REVIEWER_GATE / AWAITING
  REVIEWER PROMPT` and has no executable task.

## 2026-07-30 Phase 10L-2 Capability-Aware Planner Complete and Archived

- Added strict planner metadata for all 53 Registry entries; 38 current
  available entries can be considered, while deployment-unavailable and
  Future entries remain non-selectable.
- Added deterministic Registry snapshot, Eligibility Resolution 1.0,
  eligible-only provider projection, structured ranking, exact parameter
  binding/provenance, Capability Decision 1.0, and independent context
  validation. Only `PLAN_READY` can create a plan/job or enqueue.
- Added strict optional OpenAI-compatible selection over eligible candidates,
  one validation-guided repair, no Mock fallback, and default
  `REAL_LLM_CALLS = 0` evidence.
- Added immutable external resolution/decision/execution associations through
  Alembic 0004, additive API summaries, and an accessible PlannerWorkbench
  capability surface. AnalysisIntent remains 1.0; AnalysisPlan remains 0.1;
  PlanValidator and QueueWorkerRuntime semantics are unchanged.
- Focused contract/backend/frontend, browser matrix, performance, security,
  and evidence-integrity checks pass locally. Corrected implementation HEAD
  `9786e405f1938b514b95ccbeb1cdb6d4b26dde18` passed exact-SHA CI run
  `30511654404`: Unit, Frontend typecheck/build, PostgreSQL/Redis/MinIO
  migration/integration, and no-skipped all succeeded. Completion record
  `f62630bef53fc797705683753fbc8d5eca595c98` passed exact-SHA CI run
  `30513319990`; the verified TASKS block is archived and the permanent result
  remains in `results.md`. Phase 10L-3 is still
  `REVIEWER_GATE / AWAITING REVIEWER PROMPT`.

## 2026-07-29 Phase 10L-1 Analysis Intent Implementation Complete

- Added independent `AnalysisIntent` schema `1.0` across Python, checked-in JSON
  Schema, and TypeScript with deterministic semantic hash/ID, exact Profile 2.0
  dataset/resource/target binding, bounded vocabulary, desired outputs,
  constraints, diagnostics, and strict READY/NEEDS_CLARIFICATION/UNSUPPORTED
  consistency.
- Added deterministic and strict OpenAI-compatible Intent builders, an
  independent validator, one-round/three-question Profile-derived
  clarification, immutable revision, and typed Future/Not Planned/execution
  rejection. Default tests make zero real LLM calls and perform no silent
  repair or Mock fallback.
- Added in-memory/SQL repositories, Alembic revision 0003, additive Intent API,
  and an upstream Planner Gate. Non-READY states stop before plan/job/enqueue;
  READY passes the preserved goal to the existing Planner path and stores the
  association outside AnalysisPlan 0.1.
- Added the minimal PlannerWorkbench summary, clarification, unsupported, Run
  gate, and inert audit JSON. Chromium, Firefox, WebKit, and 390x844 mobile
  evidence pass with zero external requests and console/page errors.
- Corrected implementation HEAD `844eb149a4c528d28db9fdf70dddfaf015e91d5a`
  passed exact-SHA CI run `30425804801`: Unit, Frontend typecheck/build,
  PostgreSQL/Redis/MinIO migration/integration, and no-skipped all succeeded.
- Completion record `b4cd656e1c03bb7d6ea406ed0f2dbd828dfb2dd9`
  passed exact-SHA CI run `30426248141` with the same required gates. The
  completed queue block is archived; Phase 10L-2 remains a reviewer gate and
  is not queued.

## 2026-07-29 Phase 10L-0 Agent / Planner Capability Audit

- Audited the real Mock and optional OpenAI-compatible Planner paths,
  AnalysisPlan 0.1, Tool Registry, PlanValidator, persisted job boundary,
  QueueWorkerRuntime, PlannerWorkbench, and representative cross-domain
  prompts. This phase changes no production behavior.
- Classified the current system as `PROFILE_AWARE_SINGLE_TOOL_PLANNER` with one
  narrow sequential-independent two-tool composition. It is maturity Level 3:
  Profile-aware selection exists, but it is uneven and is not capability-aware
  multi-tool planning.
- Confirmed reusable foundations: deterministic Profile 2.0, strict Registry
  execution metadata, validated/persisted plans and hashes, sequential Runtime,
  events, artifacts, summaries, and recipes.
- Confirmed gaps: no structured Analysis Intent, no uniform Profile-to-tool
  eligibility/ranking model, no explicit step dependency or produced-artifact
  binding, no plan complexity caps, no clarification/repair contract, no
  bounded result interpretation, and no pre-execution approval/edit flow.
- Phase 10L-1 remains behind `REVIEWER_GATE / AWAITING REVIEWER PROMPT`; this
  audit does not freeze an implementation architecture or queue the next task.
- Audit commit `a7f8b14` passed exact-SHA CI run `30414233888`, including Unit,
  Frontend typecheck/build, service-backed integration, and the no-skipped
  assertion. Completion record `ee86745` passed exact-SHA CI run `30414599167`
  with the same gates. The verified Phase 10L-0 queue block is archived and
  Phase 10L-1 remains `REVIEWER_GATE / AWAITING REVIEWER PROMPT`.

## 2026-07-29 Phase 10K Material Intelligence Layer Complete

- Integrated the completed Profile 2.0, Dataset Explorer, Materials ML, and
  Composition Space products without adding a run-everything tool or moving
  scientific calculation into the browser.
- Froze one exact cross-product binding over dataset/version, Profile 2.0,
  semantic hash, full dataset content hash, and canonical resource hashes.
  Stable linked-sample identity is `objectId:sampleRef`; row/plot position is
  never used as scientific identity.
- Queue execution now resolves the exact AnalysisPlan Profile revision before
  tool execution. K4 accepts only bounded, exact-binding K3 artifacts and
  preserves source units and coverage. Ambiguous ML intent is safely exposed as
  a diagnostic state instead of falling back to guessed legacy columns.
- Added typed product states, stale-artifact rejection, settled partial refresh,
  runtime/API A-H cases, Chromium/Firefox/WebKit/mobile evidence, deterministic
  replay, near-cap performance, accessibility, network, and security evidence.
- Local full/focused checks and the browser matrix pass. Implementation commit
  `e4639a1` passed exact-SHA CI run `30382233569`; completion record `81d4446`
  passed exact-SHA CI run `30382583135`, including Unit, Frontend,
  service-backed integration, and no-skipped. The verified K5 queue block is
  archived and Phase 10K is `COMPLETE` with explicit limits. Phase 10L-0 then
  entered its audit-only gate; the dated record above supersedes the old NEXT
  status without changing the Phase 10K result.

## 2026-07-28 Phase 10K-4 Composition Space Implementation Complete

- Added the formal `dataset.composition_space` product over Profile 2.0
  formula/property semantics and explicitly bound canonical DataFrames.
- The backend builds atomic-number-ordered normalized atomic-fraction vectors,
  deterministic center-only two-dimensional PCA, optional bounded KMeans in
  feature space, explicit group/resource comparison, descriptive outlier
  candidates, property coloring, and Phase 10K-3 artifact-linked ML coloring.
- Stable identity is `objectId + sampleRef`; projection coordinates and array
  positions are never identity. Invalid formulas and partial color coverage are
  disclosed rather than silently removed.
- Added strict Registry parameters/caps, an explicit Mock Planner route,
  persisted runtime integration, an application-owned SVG/table explorer, and
  inert JSON fallback. UMAP, t-SNE, model training, scientific cluster naming,
  frontend PCA/KMeans, real LLM, external services, and Phase 10L behavior are
  unchanged.
- Runtime/API, Chromium/Firefox/WebKit/mobile, accessibility, performance,
  security, and deterministic evidence are retained. Full backend completed at
  `826 passed, 26 skipped`; frontend completed at `314 passed` with typecheck
  and build success. Implementation/evidence HEAD `fb9d720` passed exact-SHA CI
  run `30372914960`, including service-backed/no-skipped. Completion record
  `97a0781` passed exact-SHA CI run `30373474557`; the verified task block is
  archived and Phase 10K-5 remains next but unstarted.

## 2026-07-28 Phase 10K-3 Materials ML Evaluation Implementation

- Added three product-level Registry/Adapter capabilities for regression,
  uncertainty, and classification evaluation over complete Profile 2.0 semantic
  groups and one explicitly bound canonical table.
- Delivered deterministic aligned-sample metrics, fixed prediction-minus-target
  residuals, stable high-error and misclassification links, overlapping element
  and exact chemical-system diagnostics, common-sample model comparison,
  equal-count uncertainty reliability, retained-error curves, raw confusion
  counts, per-class metrics, and guarded explicit-positive binary ROC/PR.
- Added strict params and layered row/model/class/group/point/bin/artifact caps,
  Mock Planner routes, persisted runtime execution, responsive SVG/table
  products, Dataset Explorer readiness integration, and inert fallback.
- Real API/runtime evidence covers all three tools; Chromium, Firefox, WebKit,
  and mobile evidence records zero console/page errors and external requests.
  Performance evidence covers 4, 5,000, and 100,000 rows without unbounded
  display arrays. Current implementation/evidence-closure HEAD
  `a1e05ee5b0f1affa91183e681b1678d4419cedc4` passed exact-SHA CI run
  `30363719393`, including Unit, Frontend Typecheck & Build,
  PostgreSQL/Redis/MinIO service-backed integration, and the no-skipped gate.
  Completion record `c5483d6` passed exact-SHA CI run `30364098180` with the
  same gates. The verified queue task is archived; Phase 10K-4 remains next.
- No model training, embedding/clustering, real LLM, arbitrary code, dependency,
  external service, Phase 10L orchestration, or workspace redesign was added.

## 2026-07-28 Phase 10K-2 Dataset Materials Explorer Implementation

- Added the coherent `dataset.materials_explorer` product over exactly one
  Profile 2.0 plus explicitly bound table/Structure resources. It emits one
  bounded explorer bundle, quality artifact, summary, and recipe through the
  existing validated Planner/Runtime/Registry/Adapter path.
- Delivered deterministic dataset overview, composition occurrence/system
  statistics, canonical structure summaries, finite-only property
  distributions, factual quality findings, exact formula/structure duplicate
  classes, explicit group/resource comparison, and stable sample links.
- Added seven frontend result tabs with numeric/table fallbacks, responsive
  mobile layout, keyboard/accessibility coverage, and inert JSON fallback. No
  new workspace architecture or browser execution authority was introduced.
- Real persisted runtime/API evidence and Chromium/Firefox/WebKit/mobile replay
  cover mixed composition/structure/property data, partial states, explicit
  train/test comparison, 4/5,000/100,000-row performance, network isolation,
  and security. Current implementation HEAD `35c0fc6` passed exact-SHA CI run
  `30355075439`, including Unit, Frontend, service-backed, and no-skipped gates.
- Completion record `8dc2545` passed exact-SHA CI run `30355282590`; Unit,
  Frontend Typecheck & Build, service-backed integration, and no-skipped all
  succeeded. The permanent result is retained and the verified 10K-2 queue
  block is archived; 10K-3 remains not started.
- ML evaluation remains Phase 10K-3, composition space remains Phase 10K-4,
  and capability-aware planning remains Phase 10L.

## 2026-07-28 Phase 10K-1 Material Data Profile 2.0 Implementation

- Extended the existing `DataProfile schemaVersion=0.1` additively with a
  `profileContractVersion=2.0` deterministic fact layer; no parallel profile,
  new dependency, tool, Planner route, PlanValidator rule, or Runtime behavior
  was introduced.
- Centralized bounded semantic roles for formula, approved numeric properties,
  stable sample identity, regression/multiple predictions/multi-target/
  uncertainty, classification labels, and class probabilities. The old
  Planner-facing `tableSummary.inferredRole` allowlist remains exact.
- Added immutable resource semantics for table, structure/composition,
  trajectory, phonon, and volumetric normalized objects and separated data
  readiness from actual platform implementation availability.
- Added deterministic semantic hashing, dataset-version/object-hash sample
  fallback, typed ambiguity/missing reasons, explicit coverage disclosure, and
  caps of 4096 rows, 512 columns, 1024 formula values, 64 probability columns,
  and 256 resources.
- Existing upload/profile endpoints and persistence serialize the contract. A
  compact read-only frontend surface displays semantics, readiness, planned
  capabilities, coverage, and warnings.
- Focused API/unit/component checks, full local backend/frontend regression,
  typecheck/build, Phase 10 closure, and API/performance plus
  Chromium/Firefox/WebKit/mobile evidence pass. Implementation `92a8e98` passed
  exact-SHA CI run `30346512968`, including service-backed/no-skipped.
  Completion record `b5a464e` passed exact-SHA CI run `30346686652`; the
  verified 10K-1 queue block is archived and 10K-2 remains unstarted.

## 2026-07-27 Phase 10K-0 Material Intelligence Capability Gap Audit

- Audited the real parser/normalizer, `DataProfile 0.1`, Registry and adapter
  closure, Planner routing, frontend profile/results surface, artifacts,
  dependencies, caps, tests, and Phase 10A-C evidence. No product code, schema,
  tool, dependency, Planner, runtime, or frontend behavior changed.
- Classified the current profile as `MINIMAL`: table/structure summaries are a
  reusable foundation, but trajectory/phonon/volumetric discovery, material
  property semantics, model-task semantics, stable sample identity, and
  available/unavailable analyses are absent.
- Classified the Planner as `PARTIAL_PROFILE_AWARE / MOSTLY_PROMPT_ROUTED`.
  Capability-aware multi-tool planning and interpretation remain Phase 10L.
- Confirmed real executable foundations for table summaries, composition
  aggregation, lightweight structure statistics, and basic regression. Several
  historical V1 Manifest identities have no matching runtime adapter and are
  not counted as implemented.
- Froze the implementation order as 10K-1 Profile 2.0, 10K-2 Dataset Explorer,
  10K-3 ML Evaluation, 10K-4 Composition Space, and 10K-5 integration/evidence.
  Phase 10K-1 has not started.
- Audit commit `cada6fb` passed exact-SHA CI run `30270323576`, including unit,
  frontend typecheck/build, PostgreSQL/Redis/MinIO service-backed integration,
  and the no-skipped assertion. Completion record `ab5a69a` passed exact-SHA CI
  run `30270636913`; the verified 10K-0 queue block is archived and 10K-1 remains
  unstarted.

## 2026-07-27 Gate J6-R Product Roadmap Correction

- Phase 10J-6 implementation (`9cd0c69`), completion record (`75cec5f`), and
  queue archive (`16c4c18`) remain verified by successful exact-SHA CI. Its
  product readiness remains `READY_WITH_EXPLICIT_LIMITS` and its evidence and
  result history are unchanged.
- Gate J6-R supersedes the short-lived post-J6 J-7 through J-12
  electronic/Fermi roadmap without rewriting history. No scientific feature,
  schema, tool, route, runtime behavior, renderer, or dependency changed.
- The unique current route is 10K Material Intelligence, 10L Intelligent
  Analysis Agent, 10M Unified Scientific Workspace, 10N Professional Scientific
  Completion, Phase 11 validation, and Phase 12 final closure.
- CrystalNN/VoronoiNN, local environments/polyhedra, experimental XRD,
  trajectory analytics, and Electronic Band/DOS are initial-release work.
  Fermi Surface and advanced research products are Future Scope. Enterprise
  SaaS, deployment productization, and plugin marketplace are Not Planned.
- Phase 10K-0 is the next approved direction but remains unstarted until its
  complete executable prompt is supplied.

## 2026-07-27 Gate J6-A / Post-J6 Roadmap Reconciliation (Superseded)

- Phase 10J-6 implementation (`9cd0c69`), completion record (`75cec5f`), and queue archive (`16c4c18`) each have successful exact-SHA CI; its retained result and evidence establish `READY_WITH_EXPLICIT_LIMITS`.
- Repository audit confirms electronic band/DOS and Fermi Surface remain unimplemented. Existing band/DOS products are phonon-specific, and Phase 10I BZ/link contracts reserve no electronic semantics.
- At that time, continuation was frozen as J-7 through J-12. Gate J6-R later
  superseded this current-roadmap decision while retaining it as history.
- Historical J-5 ELF/Orbital and J-6 Slice/Volume names remain unchanged.

## 2026-07-26 Phase 10J-6 Volumetric Slice / Volume Rendering Completed

- Added validated three-axis exact/interpolated lattice slices with periodic wrap/non-periodic bounds, an application-owned cancellable Worker, deterministic hashes, quantitative 2D heatmap/probe/table, and true affine Three.js planes.
- Added a lazy WebGL2 Direct Volume path with canonical `width=nz,height=ny,depth=nx` R32F mapping, explicit float64 display conversion audit, bounded static ray marcher, application palettes/transfers, affine/triclinic mapping, PNG, fallback, and context/lifecycle handling.
- Added one-scene structure depth prepass and shared affine clipping for volume, atoms, bonds, and cell. Real Runtime cases cover CHGCAR charge/spin, LOCPOT, ELFCAR, PARCHG, and triclinic CUBE; Chromium near-cap `128^3` evidence uses an 8 MiB generated payload without committing it.
- Added source-native Slice decoding, true Worker termination on supersession, exact legend/table/keyboard probes, lazy perspective/orthographic 3D Slice, shader compile/link preflight, and annotated bounded Slice/Volume PNGs.
- Local closure passes 294 frontend tests, 760 backend tests with 24 intentional service-gated skips, 98 Phase 10J tests, typecheck/build, all required historical viewer runners, and real Chromium/Firefox/WebKit/mobile evidence with zero external requests. Implementation CI `30197771307` and completion-record CI `30197900247` passed unit, frontend dependency install/typecheck/build, PostgreSQL/Redis/MinIO service-backed integration, and no-skipped assertion. Queue archival was verified.

## 2026-07-24 Phase 10J-5 ELF / Orbital Product Implemented

- Added strict application-owned ELF and orbital/partial-density product mapping over unchanged Phase 10J artifacts, with decoded-value range/non-negativity validation, exact units/isovalues, full-cell statistics/integrals, source identity completeness, and no-clamp/no-renormalization boundaries.
- Reused the Phase 10J-2 Worker/Three.js renderer and added a bounded renderer-local `2x2x2` periodic structure overlay, hidden-object picking guard, scientific inspector/warnings, clipping, PNG, mobile/accessibility, and one-canvas lifecycle evidence.
- Real Mock Planner -> QueueWorkerRuntime evidence covers ELFCAR, PARCHG, and an explicitly identified CUBE; Chromium, Firefox, and WebKit all rendered WebGL2 with zero console/page errors and zero external requests. Signed amplitude, multi-orbital CUBE, ELF topology, complex phase, orbital reconstruction, and electronic identity inference remain deferred.

## 2026-07-17 Phase 10I-3 Band-BZ Linked View Completed

- Added the strict frontend-only `phase10i3.reciprocal_band_bz_link.v1` model over existing `phonon.band` and `structure.brillouin_zone` runtime artifacts; no public tool, persisted link artifact, scientific recomputation, dependency, or canonical schema was added.
- Added exact structure/primitive-lattice/convention/unit/path/discontinuity compatibility, point occurrence, segment direction, sampled q-point `t`, branch separation, bounded mapping, typed mismatch fallback, and stable provider/time-reversal warnings. Display labels are never mapping identity.
- Added one transaction-safe hover/pinned reducer, bidirectional Band/BZ selection, shared inspector/table, exact animation handoff, artifact cleanup, desktop/mobile composition, and controlled reuse of the Phase 10I-2 BZ engine.
- Closure passed 20 focused frontend link/BZ lifecycle tests, seven backend routing/runtime/evidence tests, 223 full frontend tests, and `661 passed, 23 skipped, 62 warnings` backend tests, plus typecheck/build, real Chromium 150/Firefox 128/WebKit 18 WebGL2 evidence, mobile canvas lifecycle, accessibility, near-cap mapping, zero external requests, and secret scan. Implementation/fix commits `f81aedb`, `5b5873e`, and `f3fa177` culminated in current-HEAD CI run `29572530288`, where unit, frontend/typecheck/build, service-backed integration, and no-skipped gates all succeeded.
- Completion record `02c550b67afa479ec711b45c1e9db0d61ff148b0` passed current-HEAD CI run `29572771301`; the result record was verified and the completed queue block was archived.

## 2026-07-15 Phase 10I-2 Brillouin Renderer / Evidence

- Added a strict frontend bundle mapper and outward-normal bounded face triangulation over unchanged Phase 10I artifacts; reciprocal Cartesian `angstrom^-1` values use one uniform visual scale and no repeated `2*pi` conversion.
- Added a lazy application-owned Three.js BZ engine with translucent faces, canonical edges/vertices, primitive reciprocal axes, high-symmetry points/labels/path, canonical point/face/vertex/segment picking, inspector, text tables, reciprocal-basis cameras, projection, layer/opacity/variant controls, fixed-camera PNG, fallback, context reinitialization, and complete demand-render lifecycle.
- Kept `structure.brillouin_zone` as the sole product identity and expanded explicit interactive English/Chinese routing while retaining electronic/phonon/trajectory/Fermi/mesh/magnetic/surface/editing exclusions. Artifacts still contain no renderer, shader, module, URL, texture, or network authority.
- Real PlannerWorkbench evidence passed Chromium 150, Firefox 128, WebKit 18, portrait/landscape mobile, point/face picking, PNG, context loss, accessibility, nonblank canvas, performance, console, and zero-external-network checks.
- Local closure passed 209 frontend tests, `654 passed, 23 skipped` backend tests, focused Phase 10I replay, typecheck/build, Ruff, lock/tree checks, and the historical Phase 10 three-browser product pack. Implementation commit `b5469c35cc39f096037036309a37aab160c9593c` passed CI run `29420821864`; completion record `28a3cfa934a350e5a704d9f7b35b080b354eef83` passed run `29421142527`. Unit, frontend build, service-backed integration, and no-skipped gates are closed, so the verified queue block may be archived. The configured npm audit endpoint returned `404 NOT_IMPLEMENTED`.

## 2026-07-14 Phase 10I-1 Brillouin Zone Adapter

- Registered the unique JSON-only `structure.brillouin_zone` data tool with strict single ordered/non-magnetic 3D Structure input, fixed provider policy, six inert output types, and Phase 10I caps.
- Implemented local pymatgen/spglib primitive standardization, physics-`2*pi` reciprocal construction, bounded Wigner-Seitz generator binding, Setyawan-Curtarolo paths, production provenance, validation, hashes, summary, and recipe.
- Added explicit English/Chinese planner routing, negative capability routing, PlanValidator coverage, persisted QueueWorkerRuntime replay, scientific references, typed rejection, and sanitized evidence.
- Added a fixed application-owned reciprocal/BZ/k-path/manifest JSON preview using real adapter evidence, with no canvas, graphics context, artifact execution, or renderer claim. No dependency, network, external asset, real LLM, Three.js/WebGL renderer, browser GPU evidence, or interactive BZ product was added; those remain Phase 10I-2 scope.
- Local closure passed 88 focused tests, 194 frontend tests, `648 passed, 23 skipped` backend tests, typecheck/build, Ruff, evidence replay, and the Phase 10 browser regression pack. Implementation commit `08d7742ddc6d1574a79c99baf90f019f3635aa3f` passed current-HEAD CI run `29384696711`; completion record `4defa6f4d40b074364395404451201dff21b64b5` passed run `29384954078`. Unit, frontend typecheck/build, service-backed integration, and no-skipped gates are closed, so the completed queue block is archived. The configured npm audit endpoint remains unavailable; no dependency or lockfile changed.

## 2026-07-14 Phase 10I Brillouin Zone Contract

- Added the inert `phase10i.reciprocal_lattice.v1`, `phase10i.brillouin_zone.v1`, `phase10i.kpath.v1`, `phase10i.brillouin_zone_manifest.v1`, and versioned tolerance contracts.
- Fixed row-vector physics-`2*pi` reciprocal mathematics, source/primitive/conventional transform direction, first reciprocal Wigner-Seitz topology, deterministic point/path identity, provider/time-reversal metadata, caps, hashes, and typed security validation.
- Added simple-cubic, BCC, FCC, hexagonal, triclinic, and conventional/primitive fixtures plus independent NumPy/SciPy Voronoi/ConvexHull references and Phase 10H compatibility checks.
- No production adapter, Tool Registry entry, planner route, runtime job, frontend component, Three.js/WebGL renderer, dependency, external service, or real LLM path was added.
- Local closure passed `39` Phase 10I tests, `157` focused cross-phase tests, `193` frontend tests, and `605 passed, 23 skipped` backend tests. Implementation commit `653ea133d5791db3f6879b05dc66a2e397d0d646` passed CI run `29339358234`; completion record `3fe1913b53814ef0df31f85baafa265c8ba0df97` passed CI run `29339658353`. Unit, frontend, service-backed, and no-skipped gates are closed, so the completed queue block is archived.

## 2026-07-14 Phase 10H-5 Phonon Animation

- Added formal `phonon.animation` registration and strict structure/band/eigenvector role binding through PlanValidator and QueueWorkerRuntime.
- Added inert frame-free animation package/summary/manifest/recipe, exact mode compatibility, bounded diagonal commensurate supercells, and fixed-envelope complex displacement reconstruction.
- Added app-owned Three.js phase playback, instanced periodic atoms, vectors/trails, picking inspector, exact band handoff, reduced motion, mobile, context-loss, and Chromium/Firefox/WebKit evidence.
- Completed local full regression (`193` frontend tests; `566 passed, 23 skipped` backend), typecheck/build, historical trajectory browser replay, dependency/lock review, and final security scans. The configured npm audit endpoint remains unavailable and is not reported as clean.
- Implementation commit `b67a9e18109f976aeadaf6002eaac6c71297875c` passed current-HEAD CI run `29327516331`; completion record `1021a2e2cba202ffaec22d4e0d35a4fb345a890c` passed current-HEAD CI run `29327795589`. Unit, frontend, service-backed integration, and no-skipped gates are closed, so the completed queue block is archived.

## 2026-07-14 Phase 10H-4 Phonon Eigenvector Contract

- Added inert mode/eigenvector/set/summary/manifest contracts with band hash, structure/calculation, q-point, branch, frequency, atom-order, and NAC binding.
- Fixed Cartesian complex `real[3]+imag[3]`, mass-weighted Euclidean unit norm, explicit atomic masses, canonical global phase, and phase-insensitive scientific equivalence.
- Added mass unweighting, bounded Gamma/non-Gamma static displacement reconstruction, display-only amplitude policy, small Python/NumPy/TypeScript fixtures, security, and evidence.
- Parser, adapter, tool, mode UI, commensurate-supercell solver, animation, thermal science, dependencies, network, and real LLM remain deferred.

## 2026-07-14 Phase 10H-3 Combined Band + DOS

- Added formal `phonon.band_dos` composition over validated band and DOS artifacts with ordered compatibility, source hashes, and no source mutation.
- Added exact frequency conversion, DOS density Jacobian/integral invariance, structure/atom/cell/lineage/NAC/normalization checks, and a shared union THz axis.
- Added six inert product artifacts, validated local Plotly combined preview, projection selector, tables, export, responsive accessibility, and three-browser evidence.
- Eigenvectors, animation, thermal properties, calculations, scripts, remote artifacts, dependencies, and real LLM execution remain deferred.

## 2026-07-14 Phase 10H Phonon Contract

- Added closed `phase10h.phonon_band.v1`, `phonon_dos.v1`, `phonon_summary.v1`, and `phonon_manifest.v1` contracts with deterministic Python validation and independent TypeScript consumer validation.
- Fixed row-vector `B = 2*pi*(A^-1)^T`, reciprocal-fractional q-points, explicit discontinuities, global path distance, canonical THz, negative-real imaginary modes, source-stable full `3N` branches, source-declared degeneracy, and canonical atom ordering.
- Added total/projected DOS identity and trapezoidal `3N` normalization, band/DOS compatibility, NAC/ASR provenance, application caps, inertness checks, small fixtures, independent NumPy/SciPy comparison, and reproducible evidence hashes.
- No phonon parser, adapter, formal tool, planner route, plot, renderer, eigenvector, animation, dependency, network, notebook/script, or real LLM path was added.

## 2026-07-13 Phase 10G-3 Trajectory Performance / Browser Evidence

- Registered formal `structure.trajectory_viewer` with strict planner routing, PlanValidator inputs, bounded launch options, canonical trajectory artifacts, and capability-truth metadata.
- Hardened trajectory-scoped LRU caching, one-slot seek coalescing, interactive/degraded/refused preflight, context retry, renderer metrics, mobile landscape detection, and bounded fallback output.
- Captured deterministic real parser/planner/persisted-runtime artifacts and Chromium 150, Firefox 128, WebKit 18, portrait/landscape, accessibility, lifecycle, context-loss, and rapid-seek evidence.
- Confirmed one canvas/context, bounded GPU resources and pending work, zero external requests, and no artifact execution; static-reference bonds remain `PARTIAL_READY` and indexed/chunked local storage remains deferred.

## 2026-07-13 Phase 10G-2 Trajectory Viewer

- Added validated trajectory artifact preview with real Three.js frame navigation/playback and dynamic instanced-matrix/lattice-buffer updates.
- Added stable atom/periodic instance identity, committed-frame picking/measurement and velocity/force inspection, renderer-local supercells, camera/clipping integration, bounded cache/stale guards, typed fallback, accessibility and detected mobile controls.
- Chromium, Firefox, WebKit and mobile browser smoke pass with nonblank composited-canvas checks and per-page zero-error/network audits; frontend 132 passed and backend 413 passed / 22 skipped locally.
- Static-reference bonds remain `PARTIAL_READY`; formal product registration and final bounded performance evidence were closed by Phase 10G-3.

## 2026-07-13 Phase 10G-1 Trajectory Parser / Adapter

- Added bounded streaming EXTXYZ and byte-capped canonical trajectory JSON parsers with strict UTF-8, identity, units, lattice/PBC, property, cancellation, and security checks.
- Multi-frame inputs normalize to validated `Trajectory`; single-frame EXTXYZ remains the static Structure path and plain XYZ trajectory is deferred without lattice fabrication.
- Added planner-hidden `structure.trajectory_import` validated runtime path and four inert JSON artifacts with API evidence.
- Viewer, playback, dynamic bonds, analytics, browser evidence, and formal trajectory product registration remain NOT_READY.

## 2026-07-13 Phase 10G Trajectory Contract

- Defined inert `phase10g.trajectory.v1`, frame, summary, and manifest contracts with content-derived identity and deterministic JSON.
- Fixed stable atom/frame identity, row-vector lattice math, coordinate/wrapping/time/unit semantics, strict optional properties, and application-owned caps.
- Added canonical Python validation, independent TypeScript fixture comparison, deterministic evidence, and security/network audits.
- Trajectory parsing, chunking, adapter/runtime execution, formal registration, playback, rendering, and browser/performance evidence remain NOT_READY.

## 2026-07-13 Phase 10F-25 Clipping, Cell, and Camera Controls

- Added bounded application-owned X/Y/Z clipping with shared Three.js materials and matching raycast visibility checks.
- Added independent canonical-cell, outer-supercell-boundary, and lattice-axis display with textual vector equivalents.
- Added deterministic default/top/front/side/isometric camera presets and inert `phase10f25.viewer_view_state.v1` serialization/replay validation.
- Chromium, Firefox, WebKit, and mobile evidence passed without dependency, canonical schema, topology, or backend runtime changes.

## 2026-07-13 Phase 10F-24 Supercell Productization

- Productized strict renderer-local 1x1x1 through 3x3x3 expansion with preflight, presets, outer boundary, degraded/refused states, picking, and measurement provenance.
- Added deterministic inert `phase10f24.viewer_supercell_state.v1` download/replay without canonical structure or topology mutation.
- Reused one WebGL context for expansion buffer replacement; Chromium, Firefox, and WebKit passed 20 lifecycle cycles with no console/network errors.
- Internal grid, clipping, camera presets, persisted structure supercells, trajectory, phonon, Brillouin zone, and volumetric rendering remain deferred.

## 2026-07-12 Phase 10F-15 Production Minimal Structure Viewer

- Consolidated the formal product identity on `structure.viewer_3d`; it now generates canonical inert `viewer_scene.v1` artifacts through the existing validated runtime path.
- Retained `structure.viewer_scene` for explicit JSON export and marked Phase 10D metadata/export tools as legacy direct-purpose compatibility paths.
- Replaced the active MatterViz/fallback-HTML viewer adapter behavior; formal viewer artifacts contain no HTML or executable renderer assets.
- Implemented species-grouped Three.js `InstancedMesh` atoms, bounded single-geometry bonds, renderer metrics, lazy chunk failure/retry, responsive touch controls, scene text summary, species legend, and live accessibility state.
- Aligned canonical, adapter, and renderer caps at 256 sites, 2048 bonds, 32 species, and 1 MB JSON; no renderer truncation is allowed.
- Captured live formal-tool Chromium 149, Firefox 128, and WebKit 18 WebGL 2 evidence, plus mobile, near-cap, legacy, invalid, chunk failure, unsupported, context-loss, console, network, performance, and accessibility evidence.
- Confirmed `NO_PRODUCTION_VIEWER_EXTERNAL_NETWORK_REQUESTS`.
- Corrected the Phase 10F-14 note: the attempted 3050 port drift was reverted before that phase committed; the product default port was not changed by Phase 10F-14.
- Full scientific viewer, trajectory, phonon, Brillouin-zone, volumetric rendering, editing, and advanced measurement remain deferred.

## 2026-07-11 Phase 10F-14 Validated Viewer Scene Renderer Foundation

- Selected and pinned direct `three@0.185.1` with `@types/three@0.185.1`, both MIT.
- Implemented a frontend canonical validation gate, whitelist mapper, geometry/camera utilities, Three.js renderer engine, React surface, typed fallback states, demand rendering, controls and complete disposal.
- Rendered atoms, unit cell and optional bounded bonds from live `structure.viewer_scene` artifacts.
- Added rotate, zoom, pan, deterministic reset, unit-cell toggle and bond toggle while retaining Scene JSON and Manifest preview.
- Added invalid, unsupported and context-loss fallbacks; old Phase 10D schemas remain JSON-only.
- Added mapper, geometry, component, lifecycle, security, integration and near-cap tests.
- Captured real Chrome 149 WebGL 2 evidence, interaction snapshots, live adapter API artifacts and 14 screenshots under `docs/phase10f/evidence/phase10f14_viewer_scene_renderer_foundation/`.
- Confirmed `NO_RENDERER_EXTERNAL_NETWORK_REQUESTS` and no artifact JavaScript/HTML/URL/texture/module/shader path.
- Full `structure.viewer_3d`, production-complete viewer, trajectory, phonon and Brillouin zone remain unimplemented.
- The active product frontend default port was not changed; an intermediate 3050 experiment was reverted before commit.

## 2026-07-11 Phase 10F-13 Viewer Scene Live Adapter Browser/API Evidence

- Added live adapter-backed browser/API evidence for `structure.viewer_scene`.
- Added a Python evidence generator that drives `planner_jobs`, persisted `AnalysisPlan`, `QueueWorkerRuntime.handle_job`, Tool Registry lookup, adapter execution, artifact listing, and canonical validators.
- Added a real Chrome runner that opens the existing PlannerWorkbench JSON-only preview surface using captured live adapter API responses.
- Captured live evidence for valid minimal crystal, multi-species crystal, warning/caps behavior, invalid multi-structure rejection, and manifest preview.
- Captured screenshots, DOM snapshot, console snapshot, network snapshot, API transcript, job execution audit, artifact contract audit, security audit, and schema compatibility audit under `docs/phase10f/evidence/phase10f13_viewer_scene_live_adapter_browser/`.
- Added pytest coverage for live API/runtime evidence, invalid request rejection, old/new schema routing separation, and inert/security evidence payloads.
- Confirmed old Phase 10D viewer tools remain registered and unchanged while canonical `structure.viewer_scene` remains the only `viewer_scene.v1` adapter path.
- Confirmed `NO_LIVE_ADAPTER_EXTERNAL_NETWORK_REQUESTS` for the live Chrome evidence run.
- No full `structure.viewer_3d`, WebGL renderer, Three.js integration, MatterViz renderer, renderer bundle, canvas viewer, iframe viewer, external API, notebook/script execution, real LLM path, new dependency, phonon, Brillouin-zone 3D, or artifact JavaScript was added.

## 2026-07-11 Phase 10F-12 Viewer Scene Minimal Adapter Implementation

- Implemented the canonical, renderer-free `structure.viewer_scene` adapter.
- Added Tool Registry registration with strict params and Phase 10F caps for `viewer_scene.v1`.
- Generated canonical artifacts: `viewer_scene.json`, `viewer_scene_manifest.json`, `summary.md`, and `recipe.json`.
- Reused the existing lightweight structure parser and artifact exporter; the adapter accepts exactly one periodic structure and rejects multi-structure inputs.
- Validated generated scene and manifest artifacts with the Phase 10F canonical validators before export.
- Added Mock Planner routing only for explicit inert viewer-scene JSON prompts; full viewer, WebGL, Three.js, RDF, XRD, coordination, Brillouin-zone, phonon, and trajectory prompts do not route to this adapter.
- Added adapter, registry, PlanValidator, routing, direct execution, persisted queue-runtime execution, deterministic replay, and frontend preview-regression tests.
- Added generated execution, validator, deterministic replay, preview compatibility, no-renderer, and security evidence under `docs/phase10f/evidence/phase10f12_viewer_scene_minimal_adapter/`.
- Preserved Phase 10D `structure.viewer_scene_metadata` and `structure.viewer_export_package` schemas; no silent migration or replacement was performed.
- No full `structure.viewer_3d`, WebGL renderer, Three.js integration, renderer bundle, 3D viewer component, notebook/script execution, external API, real LLM path, new dependency, phonon, Brillouin-zone 3D, or advanced local environment classifier was added.

## 2026-07-09 Phase 10F-10 Viewer Scene JSON-only Preview Surface Implementation / Evidence

- Implemented JSON-only `viewer_scene.v1` preview support in the existing PlannerWorkbench Results/export artifact preview surface.
- Added manifest preview support for Phase 10F-9 `phase10f9.viewer_scene_manifest.v1` fixtures.
- Added stable frontend evidence selectors for kind, version, schema version, validation state, error codes, warning codes, caps, scene summary, and manifest metadata.
- Added fixture-backed frontend tests covering valid, warning/caps, and invalid `viewer_scene.v1` samples.
- Added automated inertness assertions for no canvas, no script element, no iframe, no real external URL markers, no WebGL markers, and no Three.js markers.
- Added Phase 10F-10 implementation, evidence, security, browser/API boundary, readiness, and next-scope docs.
- Kept JSON-only preview evidence distinct from renderer evidence; real browser screenshot evidence remains optional future hardening.
- No full `structure.viewer_3d`, WebGL renderer, Three.js integration, renderer bundle, 3D viewer component, new adapter, planner routing change, Tool Registry runtime change, production runtime route, notebook execution, external script, external API, artifact JS, HTML renderer, phonon, Brillouin-zone 3D, or advanced local environment classifier was added.

## 2026-07-09 Phase 10F-9 Viewer Scene Contract Fixture / Validator Implementation

- Implemented a renderer-free `viewer_scene.v1` contract fixture pack under `docs/phase10f/fixtures/viewer_scene_v1/`.
- Added valid, invalid, and warning/caps fixtures for minimal crystal, multi-species crystal, optional bonds, non-finite coordinates, external-resource placeholder rejection, executable-field placeholder rejection, cap violations, and unsupported schema version.
- Added manifest fixtures and `expected_results.json` for expected validation states, error codes, warning codes, caps behavior, JSON-only preview expectation, and deferred renderer expectation.
- Added isolated contract validation utilities in `packages/artifact-core/mdi_artifact_core/viewer_scene_contract.py`.
- Added `tests/test_viewer_scene_contract_fixtures.py` to replay fixtures against the validator and manifest expectations.
- Updated shared schema notes with the implemented Phase 10F-9 validator result shape, error codes, warning codes, and fixture-pack location.
- JSON-only browser evidence remains deferred to a later evidence phase; no browser/API evidence is claimed here.
- Renderer evidence, renderer implementation, and full `structure.viewer_3d` implementation remain `NOT_READY`.
- No full viewer, WebGL renderer, Three.js integration, renderer bundle, frontend 3D runtime, new adapter, planner routing change, Tool Registry runtime change, runtime route, notebook execution, external script, external API, artifact JS, HTML renderer, external URL dependency, phonon, Brillouin-zone 3D, or advanced local environment classifier was added.

## 2026-07-09 Phase 10F-8 Viewer Scene Artifact Contract Planning

- Planned the inert `viewer_scene` artifact contract after Phase 10F-7 readiness approved a contract-before-renderer path.
- Fixed artifact identity for planning: artifact kind `viewer_scene`, contract version `viewer_scene.v1`, and schema version `phase10f8.viewer_scene.v1`.
- Planned top-level JSON fields: `kind`, `version`, `schema_version`, `source`, `metadata`, `scene`, `validation`, `caps`, `warnings`, `provenance`, and `security`.
- Planned a viewer scene manifest contract while preserving Phase 10D `viewer_assets_manifest.json` as existing static export-package evidence.
- Converted Phase 10F-7 input caps into validation-contract draft caps: `max_sites: 256`, `max_bonds: 2048`, `max_unit_cell_edges: 12`, `max_species: 32`, `max_cell_expansion: [1, 1, 1]`, and `max_scene_json_bytes: 1000000`.
- Fixed the security boundary: artifacts are inert data, with no artifact JS, no HTML, no external URLs, no remote textures, no renderer-required JSON phase, and no hidden execution path.
- Planned JSON-only browser evidence for static artifact preview; renderer screenshot evidence remains deferred and requires explicit approval.
- Decided viewer_scene artifact contract planning is `READY`.
- Decided JSON-only preview planning is `READY`.
- Decided renderer handoff is `PARTIAL_READY`.
- Decided renderer implementation is `NOT_READY`.
- Decided full `structure.viewer_3d` implementation is `NOT_READY`.
- Recommended Phase 10F-9 scope: Viewer Scene JSON Preview Evidence / Contract Fixture Planning.
- No `structure.viewer_3d`, full interactive viewer, WebGL renderer, Three.js integration, renderer bundle, frontend 3D runtime, new adapter, planner routing change, Tool Registry runtime change, notebook execution, external script, external API, artifact JS, external URL, phonon, Brillouin-zone 3D, or advanced local environment classifier was added.

## 2026-07-09 Phase 10F-7 Advanced Structure Viewer Readiness Planning

- Assessed readiness for future advanced structure viewer work after static physics implementation, browser/API evidence, and fixture-pack replay closure.
- Confirmed the static physics stack remains closed for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Used Phase 10D static `viewer_scene.json` metadata and static preview evidence as the baseline for an inert scene-artifact path.
- Proposed a future `viewer_scene.json`, `viewer_summary.md`, and `viewer_recipe.json` artifact contract path.
- Decided `viewer_scene` artifact-contract planning is ready for Phase 10F-8.
- Decided renderer implementation is `NOT_READY`.
- Decided full `structure.viewer_3d` implementation is `NOT_READY` and not approved for direct implementation.
- Kept WebGL and Three.js as future scope requiring explicit approval, sandboxing, dependency review, browser security tests, and console/network evidence.
- Kept phonon bands/DOS, Brillouin-zone 3D, and advanced local environment classification as separate future scopes.
- Official PASS claims remain none.
- Recommended Phase 10F-8 scope: Viewer Scene Artifact Contract Planning.
- No official PASS claim, notebook execution, external script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer implementation, WebGL renderer, Three.js integration, renderer bundle, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-6 Static Physics Fixture Pack Evidence Closure

- Closed the Phase 10F-5 fixture-pack replay evidence for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Retained fixture-pack replay result as `PASS`: `coordination_hist_small_crystal`, `xrd_small_crystal`, and `rdf_small_crystal` all replayed successfully through the platform/job flow.
- Confirmed candidate replay values are present in the expected contracts for selected coordination histogram, XRD, and RDF numeric checks.
- Documented the evidence boundary: fixture-pack PASS is allowed, but official examples PASS remains none because all replayed cases have `internal_regression` provenance.
- Added Phase 10F-6 closure docs, evidence boundary matrix, next-scope decision matrix, and Phase 10F-7 next-scope prompt.
- Recommended Phase 10F-7 scope: Advanced Structure Viewer Readiness Planning.
- No official PASS verification, official PASS claim, notebook execution, external script, benchmark extraction script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-5 Static Physics Fixture Pack Replay Verification

- Replayed the Phase 10F-4 static physics fixture pack through the validated platform/job flow.
- Confirmed selected tools:
  - `coordination_hist_small_crystal` -> `structure.coordination_hist`
  - `xrd_small_crystal` -> `structure.xrd`
  - `rdf_small_crystal` -> `structure.rdf`
- Verified all expected artifacts and static no-JS/no-external-URL security fields.
- Generated candidate replay values in the expected contracts while keeping every `official_pass_claim` false.
- Recorded fixture-pack replay result as `PASS`.
- Retained official PASS claims as none because all cases are `internal_regression`.
- No official PASS verification, official PASS claim, notebook execution, external script, benchmark extraction script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-4 Static Physics Direct-Uploadable Fixture Pack Construction

- Constructed a small candidate direct-uploadable fixture pack for future replay of `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Added `docs/phase10f/static_physics_fixture_pack/` with a pack README, manifest, local schemas, provenance policy, tolerance policy, and three bounded case directories.
- Added candidate cases:
  - `coordination_hist_small_crystal`
  - `xrd_small_crystal`
  - `rdf_small_crystal`
- Each case includes a small text input, `input_manifest.json`, `expected_contract.json`, `provenance.json`, and `README.md`.
- Provenance labels are `internal_regression`; all `official_pass_claim` / `official_pass_claims` fields remain `false`.
- Numeric expected values remain `pending_replay_generation` until Phase 10F-5 replays the pack through the platform/job flow.
- Added `docs/phase10f/phase10f4_static_physics_fixture_pack_construction.md` and `docs/phase10f/phase10f5_next_scope_prompt.md`.
- Recommended Phase 10F-5 scope: Static Physics Fixture Pack Replay Verification.
- No official PASS verification, official PASS claim, notebook execution, external script, benchmark extraction script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-3 Static Physics Direct-Uploadable Fixture Pack Planning

- Planned a small direct-uploadable static physics fixture pack for future replay of `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Retained Phase 10F-2 status as `PASS` and Phase 10F-1 status as `PARTIAL_PASS`; the current official benchmark pack still has zero direct-uploadable static physics official cases and no official static physics PASS claims.
- Added fixture-pack layout planning, fixture candidate matrix, provenance policy, expected-contract templates, numeric tolerance policy, fixture replay protocol, and Phase 10F-4 next-scope prompt under `docs/phase10f/`.
- Defined provenance labels for `official_direct`, `official_derived_manual`, `official_like_curated`, `internal_regression`, `mapping_only`, `future_scope`, `unsupported`, and `unknown`.
- Recorded that only `official_direct` and reviewer-approved `official_derived_manual` cases can become official PASS after direct platform replay; `official_like_curated` and `internal_regression` remain non-official regression evidence.
- Recommended Phase 10F-4 scope: Static Physics Direct-Uploadable Fixture Pack Construction.
- No fixture official PASS was generated; no notebook, external script, benchmark extraction script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-2 Official Examples Coverage Gap Closure

- Planned closure for the official static physics coverage gap found in Phase 10F-1.
- Retained Phase 10F-1 status as `PARTIAL_PASS`: the benchmark pack is present and classified, but no direct-uploadable official static physics case exists for `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`.
- Added the coverage-gap analysis, gap matrix, direct-uploadable fixture proposal, expected-contract authoring plan, and Phase 10F-3 next-scope prompt under `docs/phase10f/`.
- Recommended Phase 10F-3 scope: Static Physics Direct-Uploadable Fixture Pack Planning.
- No official static physics PASS claim was added; mapping-only, notebook-only, script-heavy, external-API, and future-scope cases remain non-PASS.
- No notebook, external script, benchmark extraction script, external API, network workflow, real LLM path, dependency installation, new adapter, adapter semantic change, Tool Registry semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, or advanced local environment classification was added.

## 2026-07-09 Phase 10F-1 Official Examples Direct Verification

- Audited the local official examples benchmark pack for direct static structure physics verification of `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Benchmark pack status: present, 61 total cases, 2 `DIRECT_VERIFIED`, 20 `MAPPING_ONLY`, 27 `EXTRACTION_REQUIRED`, and 12 `FUTURE_SCOPE`; audit status `ok: true`.
- Applied a strict direct-uploadable gate requiring local uploadable input, no notebook/script/API/network/new dependency, bounded input size, deterministic artifact comparison, and a tool mapping to one of the three completed static physics tools.
- Found no direct-uploadable official example case for `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`; no official static physics PASS claim was made.
- Recorded the two existing direct-verified official cases (`matpes_atomic_energies_csv` and `ward_metallic_glasses_csv_xz`) as unsupported for Phase 10F-1 because they are table/ML/composition cases, not static structure physics.
- Recorded structure-adjacent README/widget/Brillouin/phonon cases as mapping/future/extraction references only, not PASS.
- Added Phase 10F-1 verification docs under `docs/phase10f/official_examples_direct_verification/` and generated the Phase 10F-2 coverage-gap prompt.
- Recommended Phase 10F-2 scope: Official Examples Coverage Gap Closure.
- No new adapter, adapter semantic change, Tool Registry semantic change, Planner semantic change, QueueWorkerRuntime change, AnalysisPlanRepository change, `/planner/jobs` change, PlanValidator relaxation, full viewer, WebGL renderer, Three.js, phonon, notebook/script execution, external API workflow, real LLM path, artifact JS, or external URL loading was added.

## 2026-07-09 Phase 10F Static Structure Physics Closure

- Closed the Phase 10E static structure physics family at the implementation + browser/API evidence level.
- Completed static physics tools are `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- Verified closure across Tool Registry registration, strict params validation, deterministic static artifacts, Mock Planner routing, negative routing, browser/API evidence, no-JS/no-external-URL security posture, and CI.
- Added Phase 10F closure docs under `docs/phase10f/`, including the closure audit, next-scope decision matrix, and copyable Phase 10F-1 prompt.
- Recommended Phase 10F-1 scope: Official Examples Direct Verification for Static Structure Physics.
- No new adapter, full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, advanced local environment classification, experimental fitting, notebook/script execution, external API workflow, runtime semantic change, real LLM path, artifact JS, or external URL loading was added.

## 2026-07-09 Phase 10E-8 RDF Browser/API Evidence

- Added browser/API evidence for `structure.rdf` under `docs/phase10e/browser_api_evidence/phase10e8_rdf/`.
- Verified two small periodic structure inputs through local FastAPI `/planner/jobs`, deterministic Mock Planner, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- Confirmed `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json` were generated with Phase 10E-7 schema versions, deterministic ordering, limits/warnings, and no-JS/no-external-URL security flags.
- Captured six real browser-rendered frontend screenshots with system Chrome and Playwright `executablePath`; the frontend shows the completed RDF job, summary/recipe previews, artifact gallery entries, and `structure.rdf` ToolCall.
- Negative routing evidence confirms XRD, coordination histogram, full viewer, WebGL, Brillouin-zone, phonon, experimental PDF fitting, neutron scattering refinement, Voronoi, and CrystalNN prompts did not misroute to `structure.rdf`.
- No new adapter, full 3D viewer, WebGL renderer, Three.js, phonon, advanced local environment classification, experimental fitting, notebook/script extraction, external API workflow, runtime semantic change, real LLM path, artifact JS, or external URL loading was added.

## 2026-07-09 Phase 10E-7 RDF Implementation

- Implemented `structure.rdf` as the third Phase 10E static structure physics adapter after coordination histogram and XRD.
- The adapter uses periodic `pymatgen Structure.get_all_neighbors(r_max)` distances, fixed radial bins, `number_density` shell-volume normalization, and ordered partial RDF pairs.
- Registered strict Tool Registry params for `r_max_angstrom`, `bin_width_angstrom`, `normalization`, `include_partial_pairs`, `max_partial_pairs`, `max_sites`, `max_bins`, `max_neighbors_total`, and `plot_kind`.
- Artifacts are static and deterministic: `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json`.
- Mock Planner now routes RDF / radial-distribution / pair-distribution prompts to `structure.rdf`; XRD prompts remain `structure.xrd`, coordination prompts remain `structure.coordination_hist`, and full viewer / WebGL / phonon / fitting prompts remain deferred.
- Added unit, fixture, registry, planner-routing, artifact-contract, persisted execution, and safety tests for the adapter.
- No browser/API evidence was added; Phase 10E-8 remains responsible for end-to-end evidence.
- No full 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, advanced local environment classification, experimental fitting, notebook/script extraction, external API workflow, QueueWorkerRuntime semantic change, AnalysisPlanRepository semantic change, `/planner/jobs` semantic change, PlanValidator boundary change, new dependency, real LLM path, artifact JS, or external URL loading was added.

## 2026-07-08 Phase 10E-1 Coordination Histogram Implementation

- Implemented `structure.coordination_hist` as the first static structure physics adapter from Phase 10E planning.
- The adapter uses the existing Phase 10C/10D structure parsing path and a conservative deterministic `distance_cutoff` neighbor policy.
- Registered the tool through Tool Registry with a strict params schema for `neighbor_policy`, `cutoff_angstrom`, `max_sites`, `max_neighbors_per_site`, `include_site_details`, `group_by_element`, `include_pair_counts`, and `plot_kind`.
- Artifacts are static and deterministic: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json`.
- Mock Planner now routes coordination-number / neighbor-count prompts to `structure.coordination_hist`; XRD, RDF, full viewer, WebGL, Brillouin-zone, phonon, Voronoi, and CrystalNN prompts remain deferred.
- Added unit, fixture, registry, planner-routing, artifact-contract, persisted execution, and safety tests for the adapter.
- No browser/API evidence was added; Phase 10E-2 remains responsible for end-to-end evidence.
- No XRD, RDF, full 3D viewer, WebGL renderer, Three.js, Brillouin-zone, phonon, notebook/script extraction, external API workflow, QueueWorkerRuntime semantic change, AnalysisPlanRepository semantic change, `/planner/jobs` semantic change, PlanValidator boundary change, new dependency, real LLM path, artifact JS, or external URL loading was added.

## 2026-07-07 Phase 10C-1 Lightweight Structure Adapter Implementation

- Implemented the lightweight structure adapter batch recommended by Phase 10C:
  `structure.summary`, `structure.lattice_summary`, `structure.spacegroup_summary`,
  `structure.composition_from_structure`, and `structure.preview_metadata`.
- Registered all five tools through the Tool Registry manifest, params schemas,
  adapter exports, and adapter class registry. Execution remains
  AnalysisPlan -> PlanValidator -> persisted plan/job -> QueueWorkerRuntime ->
  Tool Registry -> Adapter -> Artifact/Result provenance.
- Dependency decision: `pymatgen`, `spglib`, and `ase` are available in the
  current environment. Structure parsing uses pymatgen `Structure` where
  possible; space-group detection uses pymatgen/spglib when available and
  returns typed dependency/detection errors instead of fabricating symmetry.
- Supported input/resource forms for this phase are bounded to platform-passed
  structure objects or text/dict payloads: pymatgen Structure, pymatgen
  Structure dict/JSON, normalized structure dict, CIF text, POSCAR/CONTCAR text,
  and small structure collections. Adapters do not read arbitrary local paths.
- Added deterministic small structure fixtures and tests for CIF, POSCAR,
  normalized dict, malformed input, missing/invalid structure handling,
  deterministic artifacts, registry schemas, planner routing, persisted job
  execution, and the 3D-viewer future-scope boundary.
- Mock Planner now routes structure prompts before generic composition/table/viz
  routing, including summary, lattice, space group, composition extraction, and
  preview metadata prompts. Explicit 3D viewer prompts are not falsely routed to
  an implemented `structure.viewer_3d`; they use preview metadata with a future
  scope rationale when appropriate.
- Generated lightweight adapter evidence under `docs/phase10c/adapter_evidence/`.
  Evidence level is Tool Registry + Adapter execution only; browser/API evidence
  is intentionally deferred to Phase 10C-2.
- No real LLM was used. No QueueWorkerRuntime main semantics,
  AnalysisPlanRepository semantics, `/planner/jobs` main semantics, or Phase 9D
  live LLM gating behavior were changed.

## 2026-07-06 Phase 10C Lightweight Structure Adapter Planning

- Completed a docs-only planning pass for lightweight structure adapters on top of the Phase 10B-2 baseline (`4a5e780`).
- Added `docs/phase10c/phase10c_lightweight_structure_adapter_planning.md` as the canonical Phase 10C planning document.
- Added `docs/phase10c/phase10c_candidate_adapter_matrix.md` to separate lightweight structure summaries from advanced structure, physics, phonon, and Brillouin zone candidates.
- Added `docs/phase10c/phase10c1_lightweight_structure_adapter_implementation_prompt.md` as the follow-on implementation prompt for Phase 10C-1.
- Recommendation: Phase 10C-1 should implement `structure.summary`, `structure.lattice_summary`, `structure.spacegroup_summary`, `structure.composition_from_structure`, and `structure.preview_metadata`.
- Reasoning: lightweight structure metadata and summaries are lower risk than 3D viewers, XRD/RDF, coordination analysis, phonon plots, and Brillouin zone rendering because they can be deterministic JSON/Markdown/recipe artifacts with bounded parser dependencies and stable CI behavior.
- Official benchmark pack remains scoped: 61 total cases, 2 `DIRECT_VERIFIED`, 27 `EXTRACTION_REQUIRED`, 20 `MAPPING_ONLY`, 12 `FUTURE_SCOPE`, audit ok with 0 issues / 0 warnings. Structure-related official examples are currently mapping-only or future-scope, not direct PASS evidence.
- No adapter implementation, runtime behavior, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator security boundary, Tool Registry execution boundary, or live LLM behavior changed in this planning phase.

## 2026-07-06 Phase 10B Second Batch pymatviz Adapter Planning

- Completed a docs-only planning pass for the second pymatviz adapter batch on top of the Phase 10A-2 baseline (`65d0c80` / `phase10a2-browser-api-evidence-baseline`).
- Added `docs/phase10b/phase10b_second_batch_adapter_planning.md` as the canonical Phase 10B planning document.
- Added `docs/phase10b/phase10b_candidate_adapter_matrix.md` to separate composition, lightweight structure, advanced structure/physics, phonon, Brillouin zone, and later ML/materials adapter candidates.
- Added `docs/phase10b/phase10b1_composition_adapter_implementation_prompt.md` as the follow-on implementation prompt for Phase 10B-1.
- Recommendation: Phase 10B-1 should focus on composition visualization adapters: `composition.ptable_heatmap`, `composition.elements_hist`, `composition.chem_sys_treemap`, `composition.chem_sys_sunburst`, and `composition.formula_statistics`.
- Reasoning: composition visualization is closer to pymatviz's materials-informatics identity than the Phase 10A table/viz batch, while remaining lower risk than WebGL structure viewers, XRD/RDF, phonon, Brillouin zone, notebook extraction, or external API workflows.
- Official benchmark pack remains `PARTIAL_BENCHMARK_READY`: 61 total cases, 2 `DIRECT_VERIFIED`, 27 `EXTRACTION_REQUIRED`, 20 `MAPPING_ONLY`, 12 `FUTURE_SCOPE`, audit ok with 0 issues / 0 warnings.
- No adapter implementation, runtime behavior, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, Tool Registry execution boundary, or live LLM behavior changed in this planning phase.

## 2026-07-06 Phase 10A-2 Browser/API Evidence for First Batch Adapters

- Added project-local evidence under `docs/phase10a/browser_api_evidence/` for the Phase 10A-1 first-batch adapters.
- Verified six scoped official direct-case scenarios with evidence level `browser_api_artifact`: MatPES scatter, MatPES histogram, Ward distribution summary, Ward histogram, Ward correlation, and Ward composition summary.
- Each scenario has redacted API captures, downloaded platform artifacts, browser-rendered Phase 9C UI screenshots, execution logs, platform summaries, artifact manifests, and evidence manifests.
- Evidence totals: 6 PASS scenarios, 60 redacted API capture JSON files, 30 PNG screenshots, and 23 artifact files. Security scanning found no `sk-`, `Bearer`, `Authorization`, `MDI_LLM_API_KEY`, `api_key`, `access_token`, or `refresh_token` hits in the evidence directory.
- Fixed the `viz.scatter` and `viz.histogram` Plotly JSON artifact contract so `scatter.json` / `histogram.json` include top-level chart metadata required by the benchmark evidence while retaining nested Plotly figure payloads.
- Tightened Mock Planner routing so composition distribution prompts route to `composition.summary` before the generic histogram/distribution branch.
- No real LLM was used for Phase 10A-2 evidence. The default CI path remains real-LLM-free.
- Phase 8B persisted-plan exact execution, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs` validate/persist/enqueue semantics, and Phase 9D live LLM gating remain unchanged.
- Remaining boundaries: the other 59 official examples are not verified by this evidence phase; browser evidence is presentation/demo evidence and is not a default CI gate; multi-step DAG/data-dependency scheduling remains future work.

## 2026-07-06 Phase 10A-1 First Batch Adapter Implementation

- Implemented the first adapter batch for the two `DIRECT_VERIFIED` official pymatviz direct cases only: `matpes_atomic_energies_csv` and `ward_metallic_glasses_csv_xz`.
- Added registry-gated tools and adapters for `table.distribution_summary`, `viz.scatter`, `viz.histogram`, `viz.correlation`, and `composition.summary`.
- MatPES routing can now produce `viz.scatter` for PBE vs r2SCAN scatter prompts and `viz.histogram` for PBE/r2SCAN distribution prompts. MatPES `ml.basic_metrics` remains unchanged for explicit numeric comparison/error-metric prompts.
- Ward routing can now produce `table.distribution_summary`, `viz.histogram`, and `viz.correlation`. `composition.summary` is available only when a stable formula/composition field is present; it must not fabricate composition results.
- Updated shared schemas to include the `viz` ToolDomain and updated frontend results rendering so new plot/table/composition artifacts appear in the Phase 9C `结果与导出` tab without changing the top/left/main-tab layout.
- Added Phase 10A-1 adapter, manifest, planner-routing, persisted-plan execution, and frontend result-display tests.
- Phase 8B persisted AnalysisPlan execution, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs` validate/persist/enqueue semantics, and Phase 9D live LLM gating remain unchanged.
- Default CI still does not call a real LLM. No API keys or external network access are introduced by these adapters.
- Remaining boundaries: browser evidence for the new tools, full official suite execution, extraction-required examples, richer report generation, multi-step DAG/data-dependency scheduling, and additional pymatviz adapters.

## 2026-07-05 Phase 9D True LLM Live Verification

- Captured redacted live-provider evidence for the OpenAI-compatible Gemini path under `docs/llm-live-verification/phase9d/`: the provider returned AnalysisPlan JSON, the plan passed PlanValidator, persisted as an AnalysisPlan, bound through `jobs.plan_id`, loaded through QueueWorkerRuntime, and executed through Tool Registry + Adapter.
- Browser evidence shows the Phase 9C UI using the live OpenAI-compatible provider, a completed job, `plan.loaded` / `data.loaded` / `tool.completed` / `job.completed`, and metrics/report artifacts. The API key was read from user environment / SecretStore only and was not recorded in docs, events, artifacts, plans, or test output.
- Live testing found that LLM output can use wrong parameter aliases even when the selected tool is valid. PlanValidator now validates each step's `params` against the registered tool `paramsSchema` before persistence; prompt tool summaries now list allowed parameter names.
- Gemini/OpenAI-compatible compatibility was tightened by omitting `response_format` for `generativelanguage.googleapis.com`, because the endpoint returned HTTP 400 for that field.
- Final gated full-chain rerun passed with Gemini 3 Flash Preview through the OpenAI-compatible Gemini endpoint: `python -m pytest -q -m llm_integration` -> `1 passed, 165 deselected`. This verified live provider JSON -> PlanValidator -> persisted AnalysisPlan -> queued worker execution -> ToolCall/Artifact/Result.
- Gemini 2.5 Flash Lite was reachable but the full-chain test returned a safe provider-side HTTP 503 during one attempt; Gemini 3 Flash Preview is the Phase 9D verified Gemini model for the current evidence.
- The user-requested Antigravity model was checked through the same Gemini AI Studio OpenAI-compatible chat/completions path. The provider returned HTTP 400 with safe message "This model only supports Interactions API", so it is not usable for the current OpenAI-compatible provider path.
- Default CI remains real-LLM-free because it does not set `MDI_RUN_LLM_INTEGRATION`.
- Redaction scans over the Phase 9D evidence found no API key, auth token header, provider key env name, or key prefix leakage.
- Remaining boundaries: production KMS/envelope encryption, multi-step DAG/data-dependency scheduling, worker supervision/dead-letter policy, and broader pymatviz adapter coverage.

## 2026-07-05 Phase 9D LLM Configuration Path Repair

- Implemented the Phase 9D configuration-chain repair without running a live LLM: explicit UI/request `PlannerUserConfig` now wins over environment model/timeout/token/temperature settings, while env-only integration tests still read `MDI_LLM_*` / `OPENAI_*`.
- Added a no-network provider resolve path for the current UI configuration. It reports whether the current planner job configuration will use Mock Planner or an OpenAI-compatible live provider, whether the selected secret exists, the effective model, and a redacted status message.
- Updated the Planner workspace model status to use the current UI provider resolution instead of treating the default env provider status as the selected task provider.
- Added a gated full-chain live LLM test path that, when env is configured, uploads a tiny metrics CSV, requests a live OpenAI-compatible plan, persists the validated AnalysisPlan, runs the queued job, and verifies ToolCall/Artifact/Result provenance.
- The live test was not executed locally because live LLM env is not configured; the default run correctly skips it.
- No QueueWorkerRuntime, AnalysisPlanRepository, Tool Registry manifest, adapter implementation, migration, or `/planner/jobs` persistence/enqueue semantics changed.

## 2026-07-05 Phase 9C Browser Visual QA and Official Direct Re-verification

- Ran a real browser-controlled Phase 9C visual QA against the local workspace at `http://127.0.0.1:3000` with API `http://127.0.0.1:8000`, local SQLite/runtime queue, local ArtifactStorage, and Mock Planner only.
- Saved Phase 9C browser QA screenshots under `docs/ui-redesign/phase9c_browser_qa/`:
  `01_workspace_default.png`, `02_data_context_viewer.png`, `03_agent_process_tab.png`,
  `04_chat_plan_tab.png`, `05_results_export_tab.png`, and `06_developer_mode.png`.
- Verified the UI visually follows the Phase 9C baseline: top global dataset/model/job bar, left data-context viewer, and exactly one active main tab among `Agent 过程`, `对话与 Plan`, and `结果与导出`. No independent right result panel, right Agent panel, or bottom result tabs were used.
- Re-deleted and regenerated fresh Desktop evidence for the two official direct-uploadable pymatviz cases using the Phase 9C UI:
  - `matpes_atomic_energies_csv`: dataset `dataset_0004`, profile `profile_dataset_0004_v1`, job `job_c6e8034a138f469da0d72f2e`, plan `plan_202acca0e0c74d5fa7a0f794`, planHash `a205a4de5017e47c47358d1f97ca919d5d5db926920520a3430468c7867e0dfe`, tool `ml.basic_metrics`, artifact `metrics.json`, verdict `PASS_WITH_CURRENT_PLATFORM_SCOPE`.
  - `ward_metallic_glasses_csv_xz`: dataset `dataset_0005`, profile `profile_dataset_0005_v1`, job `job_3c6b5797a14e4732bf19c64d`, plan `plan_017cf930f0224728bb3850b5`, planHash `4c16e617ea4c6efc727f81d7b0915fe6ee6e92191b98ae41a558713c1bbde9c2`, tool `table.numeric_summary`, artifacts `numeric_summary.json`, `summary.md`, and `recipe.json`, verdict `PASS_WITH_CURRENT_PLATFORM_SCOPE`.
- The official example evidence pack was updated at `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite`, but that Desktop evidence pack is not part of the project Git commit. Only the Phase 9C QA screenshots under `docs/ui-redesign/phase9c_browser_qa/` are intended for commit.
- True LLM was not used; no API key was entered or captured.

## 2026-07-05 Phase 9C UI/UX Redesign Implementation Baseline

- Implemented the Phase 9C frontend layout in `apps/web/app/components/PlannerWorkbench.tsx`: top `GlobalContextBar`, resizable/collapsible left `DataContextViewer`, and a main workspace with exactly three mutually exclusive tabs.
- Top bar now opens dataset/profile and model/provider dialogs. Dataset dialog supports dataset selection, manual IDs, demo dataset loading, upload, and profile generation. Model dialog supports Mock/OpenAI-compatible mode, provider preset/config fields, Secret selection/creation/deletion, and safe provider test.
- Left `DataContextViewer` is now a viewer rather than a control column. It adapts rendered profile content for table, structure, archive/object, and unsupported/partial states, and supports collapse plus drag resize.
- Main workspace tabs are `Agent 过程`, `对话与 Plan`, and `结果与导出`; only the active tab is rendered. There is no independent right status/result column and no bottom result tab strip in the Phase 9C implementation.
- Conversation uses selectable chunks for user request, Plan Preview, validation, run status, and result references. Chunk selection drives the result context used by `结果与导出`.
- Results/export tab now owns report/recipe summary, 3D material result placeholder, metrics result, table/numeric summary, Artifact Gallery, ToolCalls, and export/download controls. It shows `请选择一个分析步骤或结果 chunk` when no chunk is selected.
- Agent process tab shows structured JobEvents including `plan.loaded`, `data.loaded`, `tool.started`, `tool.completed`, and `job.completed`, with safe payload disclosure and persisted-plan/Tool Registry/no-fallback provenance.
- Updated frontend tests to cover the strict top/left/main-tab layout, dataset/model top dialogs, Secret no-leak behavior, left data viewer, mutually exclusive main tabs, Agent process evidence, results/export evidence, validation-failure no plan/job/enqueue, and no broad `Not available yet` UI.
- Phase 8B/9A execution boundaries remain unchanged: no backend route, QueueWorkerRuntime, AnalysisPlanRepository, Tool Registry, Adapter, provider security, migration, or CI behavior was changed.

Verification so far:

- `npm run typecheck` in `apps/web`: passed.
- `npm test` in `apps/web`: 6 passed.
- `npm run build` in `apps/web`: passed.
- `uv lock --check`: passed.
- `python -m pytest tests/test_phase7_llm_planner.py -q`: 32 passed.
- `python -m pytest tests/test_phase8b_persisted_plan_queue.py -q`: 9 passed / 1 skipped locally.
- `python -m pytest tests/test_phase8c_planner_read_api.py -q`: 2 passed.
- `python -m pytest tests/test_phase9b_demo_workspace_api.py -q`: 15 passed.
- `python -m pytest -q`: 138 passed / 21 skipped.
- `git diff --check`: passed with Windows line-ending warnings only.

## 2026-07-05 Phase 9C UI/UX Redesign Docs Baseline

- Updated the frontend design baseline to the user-specified AI assistant workspace layout: top global dataset/model context bar, collapsible/resizable left data-context viewer, and a main workspace with exactly three mutually exclusive tabs.
- The three main tabs are now canonical: `Agent 过程`, `对话与 Plan`, and `结果与导出`. The independent right-side Result Inspector, legacy right Agent panel, and bottom result panel are no longer recommended implementation targets.
- Results are now documented as part of the main `结果与导出` tab: report summary, 3D material view, metrics, table/numeric summary, Artifact Gallery, Recipe/provenance, report export, and artifact download all live there.
- Added UI-only view model names for `MainWorkspaceTab`, `ConversationChunkView`, `DataContextViewerState`, and `SelectedResultContext` in the shared schema document without changing backend persistence schema.
- Preserved core execution boundaries: LLMs still produce JSON AnalysisPlans only; valid plans still pass PlanValidator, persist as AnalysisPlans, bind through jobs, load in QueueWorkerRuntime, and execute through Tool Registry + Adapter.
- This round is docs-only. No API, Worker, Tool Registry, Adapter, frontend implementation code, tests, migrations, or CI configuration were changed.

## 2026-07-05 Phase 9B Official Direct Examples Semantic Refinement

- Added a minimal `table.numeric_summary` MVP tool and adapter for semantically correct table statistics on official direct-uploadable tabular examples.
- Ward metallic glasses now routes through `table.numeric_summary` for independent numeric column summaries (`D_max`, `dTx`) plus categorical summaries (`material_id`, `composition`, `gfa_type`) instead of treating `D_max` and `dTx` as target/prediction regression columns.
- MatPES remains routed through `ml.basic_metrics` with DataProfile-bound `targetColumn=PBE` and `predictionColumn=r2SCAN`; fresh browser evidence no longer contains the stale `y_true` / `y_pred` prompt.
- Re-generated fresh browser evidence for `matpes_atomic_energies_csv` and `ward_metallic_glasses_csv_xz` after deleting each case's old `results/` directory. Both runs used Mock Planner only, created fresh persisted AnalysisPlans, loaded plans through QueueWorkerRuntime, emitted `plan.loaded` / `data.loaded` / `tool.completed` / `job.completed`, and saved API responses, artifacts, screenshots, and summaries.
- Phase 8B/9A boundaries remain unchanged: no QueueWorkerRuntime redesign, no AnalysisPlanRepository change, no `/planner/jobs` persistence/enqueue bypass, no real LLM call, and no execution outside Tool Registry + Adapter.

## 2026-07-04 Phase 9B Official MatPES Example Blocker Repair

- Fixed the blocker found by the official pymatviz examples evidence pack: `matpes_atomic_energies_csv` uploaded and profiled correctly, but Mock Planner hard-coded `targetColumn=y_true` / `predictionColumn=y_pred`, causing `ml.basic_metrics` to fail for the official MatPES columns `element`, `PBE`, and `r2SCAN`.
- Updated `MockLLMProvider` so default mock plans bind `ml.basic_metrics` params from the real `DataProfile`: target/prediction role columns win first, and tables with no explicit roles fall back to the first two numeric columns. The provider still emits only structured AnalysisPlan JSON; it does not execute code or bypass validation.
- Added a regression proving a MatPES-style uploaded CSV (`element,PBE,r2SCAN`) goes through `/planner/jobs`, persists an AnalysisPlan with `targetColumn=PBE` and `predictionColumn=r2SCAN`, runs through QueueWorkerRuntime, executes one real `ml.basic_metrics` ToolCall, creates one metrics artifact, and reaches `completed`.
- Re-ran the failed browser evidence case with the full official MatPES CSV: 89 rows, columns `element`, `PBE`, `r2SCAN`, `job_b81c14bde6c3479599e19312`, `plan_4117360927074c8fad3ec8f3`, `planHash=ce6322d32f52b25913e9d4ae14aa535eb91704648eb5ea3ca684db0e8620bef8`, one completed ToolCall, one `metrics_json` artifact, and timeline events `plan.loaded`, `data.loaded`, `tool.started`, `artifact.ready`, `tool.completed`, `job.completed`.
- Evidence pack updated under `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite`: `matpes_atomic_energies_csv` now has four browser screenshots and `platform_result_summary.md` is PASS. The full 61-case official suite is still not claimed complete; this repair verifies the previously failed blocker.
- Verification: `uv lock --check` passed; Phase 7 targeted 32 passed; Phase 8B targeted 9 passed / 1 skipped locally; Phase 8C targeted 2 passed; Phase 9B targeted 14 passed; backend full 136 passed / 21 skipped; frontend `npm test` 6 passed; frontend typecheck passed; frontend build passed after stopping the old dev server that held `.next/trace`.
- Remaining follow-up: continue the rest of the official examples suite separately.

## 2026-07-04 Phase 9B Browser + Durable Worker Resolver Closure

- Completed the browser click-through that was previously blocked by the browser native bridge. The in-app browser now loaded `http://127.0.0.1:3000`, loaded the backend demo dataset, created and ran a Mock Planner job, and showed `completed` status with persisted-plan provenance.
- Browser evidence: the UI displayed `Demo metrics dataset`, profile columns `formula, y_true, y_pred`, `planId`, `planHash`, `jobs.plan_id -> analysis_plans.id`, `Loaded from persisted AnalysisPlan`, `Executed through Tool Registry + Adapter`, `No deterministic fallback used`, `plan.loaded`, `data.loaded`, `tool.started`, `artifact.ready`, `tool.completed`, and `job.completed`.
- Browser result panels were verified: Artifact Gallery showed one `metrics.json` artifact, Report / Recipe Summary showed a system-generated summary and reproducibility fields, and Tool Calls showed one completed `ml.basic_metrics` call with `stepId=llm_step_1` and plan provenance.
- Added a durable worker object-store resolver for out-of-process queue workers. It rebuilds `ml_table`, `structures`, and `formulas` from persisted dataset `metadata.normalizedExports` plus ArtifactStorage, instead of relying on API-process memory.
- Added settings-driven worker runtime construction for `run_queued_job(job_id)`: it now builds SQLAlchemy repositories from `DATABASE_URL`, artifact storage from `MDI_ARTIFACT_BACKEND` / `MDI_ARTIFACT_ROOT`, and the durable resolver before executing `QueueWorkerRuntime.handle_job(job_id)`.
- Connected the same durable resolver into the PostgreSQL planner runtime path so local PostgreSQL/in-memory-queue development and Redis enqueue paths use the same dataset-object loading seam.
- Added `MDI_ARTIFACT_ROOT` config support and a shared `create_artifact_storage_from_settings()` helper.
- Added a regression proving `run_queued_job(job_id)` can run as a separate settings-driven worker against a persisted SQLite repository and local ArtifactStorage: it reconstructs `ml_table` from normalized exports, loads the persisted AnalysisPlan, executes exactly one real `ml.basic_metrics` adapter call, emits `data.loaded` / `plan.loaded`, writes one artifact, and completes the job.
- Verification: browser UI assertions passed with no console errors and no `Not available yet` in the rendered page; Phase 9B targeted passed with 13 tests; Phase 9B + Phase 8B targeted passed with 22 passed / 1 skipped; Phase 7 + Phase 8C targeted passed with 34 tests; backend full passed with 135 passed / 21 skipped; frontend `npm test` passed with 6 tests; frontend typecheck and build passed.
- Live true-LLM verification is still not claimed; no API key was entered during the browser run and no external LLM call was made.
- Remaining production boundary is narrowed: worker-side durable loading is implemented, but a fully production upload service that writes normalized exports directly through SQL/MinIO rather than the Phase2 in-memory runtime remains future hardening.

## 2026-07-04 Phase 9B Runtime Data Binding Follow-up

- Closed the practical demo gap found during full Planner workspace testing: in the local in-memory development path, `enqueue=true` created and enqueued a planner job but no separate worker drained the queue, so the UI could remain in the queued state even though the plan/job APIs were valid.
- Added a narrow local-only auto-drain path for `/planner/jobs`: when the app is using the default in-memory repositories/runtime and no Redis queue URL is configured, the planner route enqueues the job and then immediately runs `QueueWorkerRuntime.handle_job(job_id)`. This does not affect the PostgreSQL/Redis production path, injected test runtimes, or Phase 8B service-backed queue semantics.
- Added dataset object binding from the Phase2 runtime into `QueueWorkerRuntime`. The worker can now resolve uploaded/demo dataset objects by `dataset_id`, inject them as the execution `object_store`, and emit a `data.loaded` JobEvent before loading the persisted plan.
- Added Phase2 runtime accessors for the real uploaded `DataProfile` and normalized dataset object store. Planner preview/jobs now prefer the real Phase2 profile instead of a minimal synthetic profile when the dataset exists.
- Tightened planner validation for executable uploaded datasets: ML plans must bind `ml_table`, structure plans must bind `structures`, and composition plans must bind `formulas` when those normalized objects exist. Missing or unresolved inputRefs are rejected before any AnalysisPlan persistence, Job creation, or enqueue.
- Updated the planner prompt to describe the normalized inputRef conventions (`ml_table`, `structures`, `formulas`) so real OpenAI-compatible providers are steered toward executable plans without relying on prompt text as a security boundary.
- Added regression coverage proving an uploaded CSV dataset can create an enqueued local planner job, auto-run through the persisted AnalysisPlan path, produce exactly one `ml.basic_metrics` ToolCall, emit `data.loaded`/`plan.loaded`, create an artifact/result, and reach `completed`.
- Added regression coverage proving a valid-looking plan with missing `inputRefs` is rejected for an uploaded dataset and creates no plan, no job, and no enqueue.
- Reorganized supported pymatviz sample cases under `C:\Users\86182\Desktop\pymatviz-web-test-cases`, with each case split into `raw_data/` and `results/`. Four true data samples were evaluated successfully through the platform path: MatPES CSV metrics, MP structure JSON, experimental Bi2Zr2O7 CIF, and MP Zr2Bi2O7 CIF.
- Verification for this follow-up: Phase 9B API targeted passed with 12 tests; Phase 8B targeted passed with 9 passed / 1 skipped locally; Phase 7 + Phase 8C + Phase 9B targeted passed with 46 tests; backend full passed with 134 passed / 21 skipped; frontend `npm test` passed with 6 tests; frontend typecheck and build passed after restarting the old dev server that held `.next/trace`.
- Post-restart API smoke verified CORS preflight, `/health/runtime`, provider APIs, demo dataset creation, and `/planner/jobs` local enqueue execution. A demo planner job returned `enqueued=true`, `executed=true`, status `completed`, exactly one ToolCall, one artifact, and a completed result.
- Browser plugin control was unavailable in this Codex environment after restart, so the final UI click-through was not claimed. Verification is based on API E2E, frontend tests, and backend tests.

## 2026-07-04 Phase 9B Frontend/API Follow-up

- Re-audited the Planner workspace API calls against backend route registration after browser logs showed `OPTIONS ... 405 Method Not Allowed`.
- Confirmed the affected API routes existed; the failure was missing CORS preflight handling for cross-port browser access, not missing GET/POST implementations.
- Added FastAPI `CORSMiddleware` with configurable local/demo origins and coverage for the Phase 9B workspace routes.
- Hardened `/health/runtime` so runtime status is based on safe light probes where configured instead of static configuration inference only. Failed database, Redis, or MinIO probes return `unknown` with class-level safe reasons and no credential-bearing URLs or keys.
- Tightened `/planner/jobs` validation-failure behavior so rejected raw plans are not returned in the response. Invalid plans still create no AnalysisPlan, no Job, and no enqueue, and now also avoid echoing credential-like params.
- Completed the Phase 9B i18n cleanup follow-up by moving remaining user-facing Chinese labels from `PlannerWorkbench.tsx` into message dictionaries and adding English-mode assertions.
- Verification after the follow-up: `python -m pytest tests/test_phase9b_demo_workspace_api.py -q` passed with 10 tests; Phase 7 targeted passed with 32 tests; Phase 8B targeted passed with 9 passed / 1 skipped locally; Phase 8C targeted passed with 2 tests; backend full passed with 132 passed / 21 skipped; frontend `npm test` passed with 6 tests; frontend `npm run typecheck` and `npm run build` passed.

## 2026-07-04 Phase 9B Demo-ready AI Planner Workspace

- Upgraded the Planner workspace from an engineering/debug view into a demo-ready product workspace while preserving the Phase 8B persisted-plan execution contract and the Phase 9A gated provider safety boundary.
- Added a default `zh-CN` frontend i18n layer with an English toggle. The main workspace now uses localized labels, empty states, error guidance, timeline labels, provider/health labels, artifact labels, and report/recipe labels instead of broad `Not available yet` placeholders.
- Added a productized Planner layout: top runtime/status strip, left data/provider controls, central prompt/plan/run area, right health/provenance/timeline area, and bottom tabs for result overview, artifact gallery, report/recipe summary, tool calls, and developer audit.
- Added API-backed runtime health, dataset detail, demo dataset/profile, provider catalog/status/test, and extended Secret UX support. The demo dataset/profile path is generated through the backend Phase2 runtime, not faked in the frontend.
- Added `LLMProviderSettingsPanel` behavior for mock vs OpenAI-compatible modes, OpenAI/DeepSeek/custom presets, Secret save/list/delete, and safe provider connection tests that use `secretId` server-side. API keys are not stored in localStorage/sessionStorage and are cleared from the input after save.
- Added a Chinese Error Explainer and validation failure UX that clearly states: no AnalysisPlan was saved, no Job was created, and nothing was enqueued.
- Added user/developer mode layering. User mode shows task-oriented plan/result summaries; developer mode exposes raw AnalysisPlan JSON, JobEvents, ToolCalls, Artifacts, API responses, `planId`, `planHash`, and storage/provenance identifiers.
- Productized results: Artifact Gallery is grouped by chart, JSON metrics, table, structure, report file, and other; Report/Recipe Summary is a separate system-generated summary tied to dataset/profile/AnalysisPlan/tool calls/artifacts/provenance.
- Added Phase 9B backend tests for runtime health, demo dataset/profile, provider catalog/status/test, Secret list no plaintext, provider error redaction, and planner validation failure no plan/job/enqueue.
- Added Phase 9B frontend tests for default Chinese rendering, language switch, region-specific empty states, demo dataset loading, profile summary, provider settings, Secret UX no key leakage, provider test success/failure, SSE timeline, artifact grouping, report/recipe summary, developer audit, and validation-failure no plan/job/enqueue.
- Local verification before commit: `uv lock --check` passed; Phase 7 targeted 32 passed; Phase 8B targeted 9 passed / 1 skipped locally; Phase 8C read API targeted 2 passed; Phase 9B API targeted 7 passed; backend full 129 passed / 21 skipped; frontend `npm test` 6 passed; `npm run typecheck` passed; `npm run build` passed.
- Live LLM verification is still not claimed; no `MDI_RUN_LLM_INTEGRATION=1` live-provider run was executed in this Phase 9B work.
- Remaining boundaries after Phase 9B: production secret encryption/KMS, multi-step DAG/data-dependency execution, worker supervision/dead-letter policy, advanced material viewer polish, and live true-LLM verification when env is explicitly configured.

## 2026-07-03 Phase 9A True LLM Provider Gated Integration

- Added a gated OpenAI-compatible LLM provider path for planner generation. The default planner path remains `MockLLMProvider`; real network calls require explicit `provider="openai_compatible"` or `MDI_LLM_PROVIDER=openai_compatible`.
- OpenAI-compatible provider configuration is resolved at call time from `MDI_LLM_BASE_URL`, `MDI_LLM_API_KEY`, `MDI_LLM_MODEL`, `MDI_LLM_TIMEOUT_SECONDS`, `MDI_LLM_MAX_TOKENS`, and `MDI_LLM_TEMPERATURE` (with legacy `OPENAI_*` fallbacks for compatibility).
- Provider outputs still parse to JSON first and then pass through the existing strict `PlanValidator`; invalid schema, non-JSON completion, unknown/non-MVP tools, duplicate/empty steps, and credential-like params remain rejected before any plan/job/queue mutation.
- `/planner/jobs` keeps the Phase 8B persisted-plan contract: validation success persists the exact validated `AnalysisPlan`, creates a `job.plan_id` binding, and optionally enqueues only `job_id`; validation/provider failure returns no `plan_id`, no `job_id`, and no enqueue.
- Safe provider errors now cover missing key, timeout, network failure, HTTP 401/429/5xx, and malformed provider response without exposing API keys or raw environment details. Raw prompt/completion is not persisted to `analysis_plans`, JobEvents, Artifacts, or Results.
- Added fake-transport tests for OpenAI-compatible success, markdown-fenced JSON, non-JSON completion, HTTP errors, timeout, missing key, default no-network behavior, provider validation failure no-op, and valid provider output entering the persisted-plan path.
- Added a gated `llm_integration` pytest marker and live test. It only runs when `MDI_RUN_LLM_INTEGRATION=1` and required `MDI_LLM_*` env vars are present; otherwise it skips with a clear reason. Default CI does not require or call a real LLM.
- Local verification: `uv lock --check` passed; `python -m pytest tests/test_phase7_llm_planner.py -q` passed with 32 tests; `python -m pytest tests/test_phase8b_persisted_plan_queue.py -q` passed with 9 passed / 1 skipped; `python -m pytest tests/test_phase8c_planner_read_api.py -q` passed with 2 tests; `python -m pytest -q` passed with 122 passed / 21 skipped; `npm ci`, `npm test`, `npm run typecheck`, and `npm run build` passed in `apps/web`.
- Local live LLM verification was not run because `MDI_RUN_LLM_INTEGRATION` and provider credentials are not configured. `python -m pytest -q -m llm_integration` skipped 1 test and made no external LLM call.
- Local machine has no Docker CLI, so service-backed PostgreSQL + Redis + MinIO integration remains CI-backed for this phase until the Phase 9A commit is pushed.
- Remaining boundaries after Phase 9A: production secret encryption/KMS, multi-step DAG/data-dependency execution, worker supervision/dead-letter policy, and advanced material viewer polish.

## 2026-07-03 Phase 8C-P1 Frontend Planner UX Compliance Closure

- Closed the Phase 8C P1 docs-compliance gaps without entering Phase 9 and without changing QueueWorkerRuntime, AnalysisPlanRepository, or the core `/planner/jobs` validate/persist/enqueue semantics.
- Added an EventSource-backed planner timeline path using the read-only SSE endpoint `/planner/jobs/{job_id}/events/stream`. The UI still keeps polling as a fallback, but the primary timeline transport now uses persisted JobEvents and highlights `plan.loaded`.
- Added an independent `Report / Recipe Summary` panel. Artifact gallery is now separate from report/result/recipe summary; the summary panel displays result summary, report artifacts, recipe artifacts, artifact references, `planId`, `planHash`, and persisted-plan provenance.
- Upgraded the Planner workbench data context entry from raw IDs only to an API-backed Dataset/Profile selector using existing `/datasets` and `/datasets/{dataset_id}/profile` reads, while preserving manual ID fallback and avoiding fake dataset/profile records.
- Added read-only SSE replay support for planner JobEvents. The endpoint replays persisted events only; it does not mutate jobs/plans, enqueue work, execute tools, or call deterministic fallback planning.
- Frontend tests now cover EventSource/SSE timeline behavior, Report/Recipe Summary rendering, Dataset/Profile selector behavior, validation-failure no-save/no-job/no-enqueue semantics, loading state, and API error state.
- Local verification for this closure: `uv lock --check` passed; `python -m pytest tests/test_phase8c_planner_read_api.py -q` passed with 2 tests; `python -m pytest tests/test_phase8b_persisted_plan_queue.py -q` passed with 9 passed / 1 skipped; `python -m pytest -q` passed with 112 passed / 20 skipped; `npm test` passed with 5 frontend tests; `npm run typecheck` and `npm run build` passed in `apps/web`.
- Phase 8C-P1 implementation commit `4d0c241` passed GitHub Actions run `28664159687`: Unit Tests, Frontend Typecheck & Build, and Service-backed Integration all succeeded. The integration job reported 19 passed, 0 skipped, 0 failed.
- Phase 8C-P1 status: PASS / compliance closure accepted after CI-backed verification.
- Remaining boundaries are unchanged: true LLM integration, advanced multi-step DAG/data-dependency execution, production secret encryption, worker supervision/dead-letter policy, and advanced material viewer polish.

## 2026-07-03 Phase 8C Frontend Planner UX Update

- Phase 8B is the frozen baseline for this work: final freeze commit `03d1915` (`Record phase 8B acceptance freeze`) after Phase 8B code commits `75386cf`, `9b62fa1`, `336fd8b`, and `962c429`; GitHub Actions run `28637798200` succeeded.
- Added a real frontend Planner workbench entry point instead of the previous static shell. Users can enter `projectId`, dataset/profile identifiers, a natural-language analysis request, and choose whether to enqueue the planner job.
- Added a typed frontend planner API client for `POST /planner/jobs` plus read-only planner detail endpoints for persisted AnalysisPlan, job detail, JobEvents, ToolCalls, Artifacts, and result summary.
- Added minimal read-only backend planner endpoints under `/planner/...` so the frontend can display persisted-plan provenance without mutating plans/jobs, enqueueing work, or triggering execution.
- The success UI now shows the validated persisted plan preview, `job_id`, `plan_id`, backend `plan_hash`, `job.plan_id -> analysis_plans.id`, step count, `stepId`, `toolId`, validation status, and plan source.
- The provenance UI now displays persisted-plan binding, `plan.loaded` JobEvent when present, ToolCall `planId`/`planHash`, Artifact `planId`/`planHash`, Result `planId`/`planHash`, and the statements "Loaded from persisted AnalysisPlan", "Executed through Tool Registry + Adapter", and "No deterministic fallback used" only when backed by returned API data.
- The validation failure UI now clearly states: "Plan validation failed", "No AnalysisPlan was saved", "No Job was created", "Nothing was enqueued", and "Please fix the request and try again"; it clears job state and does not start status polling.
- No true LLM integration, multi-step DAG execution, production secret encryption, QueueWorkerRuntime redesign, AnalysisPlanRepository redesign, or Tool Registry redesign was introduced.
- Local verification for the Phase 8C implementation: `uv lock --check` passed; `python -m pytest tests/test_phase8c_planner_read_api.py -q` passed with 2 tests; `python -m pytest tests/test_phase8c_planner_read_api.py tests/test_phase8b_persisted_plan_queue.py -q` passed with 11 passed / 1 skipped; `python -m pytest -q` passed with 112 passed / 20 skipped; `npm ci`, `npm test`, `npm run typecheck`, and `npm run build` passed in `apps/web`.
- Phase 8C implementation commit `9967c5b` passed GitHub Actions run `28646226271`: Unit Tests, Frontend Typecheck & Build, and Service-backed Integration all succeeded. The integration job reported 19 passed, 0 skipped, 0 failed.
- Phase 8C status: PASS / baseline frozen after CI-backed verification.
- Remaining boundaries after this update: true LLM integration, advanced multi-step DAG/data-dependency execution, production secret encryption, worker process supervision/dead-letter policy, and deeper material-specific viewer polish.

## 2026-07-03 Phase 8B Persisted Plans + Queue Worker Update

- Added PostgreSQL-backed `analysis_plans` persistence and `jobs.plan_id` linkage through Alembic revision `0002_phase8b_plans`.
- Added `AnalysisPlanRepository` to both in-memory and SQLAlchemy repository bundles, including `save_plan`, `get_plan`, `get_plan_for_job`, `attach_plan_to_job`, AnalysisPlan JSON round-trip, canonical SHA-256 `plan_hash`, and credential-key rejection before persistence.
- Upgraded `POST /planner/jobs` to validate first, persist the exact validated `AnalysisPlan`, create a Job linked by `plan_id`, and optionally enqueue only `job_id`; it no longer synchronously executes in the planner route.
- Upgraded `QueueWorkerRuntime.handle_job(job_id)` so the main path loads `job.plan_id`, reconstructs the persisted `AnalysisPlan`, executes exactly `plan.steps`, and writes ToolCall, JobEvent, Artifact, and completed Job status with `planId`/`planHash` provenance.
- Preserved explicit fallback only for dev/test jobs without a persisted plan. When `plan_id` exists, persisted plan loading wins and `build_phase2_plan` is not used.
- Core evidence: `tests/test_phase8b_persisted_plan_queue.py` proves persisted 1-step plan -> exactly 1 ToolCall, `toolId=ml.basic_metrics`, `stepId=llm_step_1`, Artifact generated, `plan.loaded` JobEvent includes `planId`/`planHash`, and Job reaches `completed`. The targeted suite also covers the real `ml.basic_metrics` adapter path without a fake executor.
- Verification: `uv lock --check` passed; Phase 8B targeted 9 passed / 1 skipped; Phase 8A 11 passed; Phase 7 22 passed; backend full 110 passed / 20 skipped; frontend `npm ci`, `npm run typecheck`, and `npm run build` passed.
- Local machine has no Docker CLI, so service-backed Phase 8B integration could not be run locally. GitHub Actions run `28631817086` on Phase 8B code acceptance commit `962c429` passed all three jobs; the service-backed PostgreSQL + Redis + MinIO job reported 19 passed, 0 skipped, 0 failed, including the Phase 8B persisted-plan queue test.
- Phase 8B acceptance: PASS / frozen. Phase 8C frontend Planner UX may start next, but true LLM integration, multi-step DAG/data-dependency execution, production secret encryption, and worker process supervision/dead-letter policy remain out of scope.
- Remaining boundaries after Phase 8B: true LLM integration, frontend Planner UX (Phase 8C), multi-step DAG/data-dependency execution, production secret encryption, worker process supervision/dead-letter policy.

## 2026-06-27 Phase 8A LLM Plan Execution Bridge Update

- Closed the largest Phase 7 boundary: validated LLM AnalysisPlans now actually execute, instead of being discarded in favor of the deterministic plan.
- `Phase2ProductRuntime.create_job` gained two parameters: `analysis_plan` (use this EXACT validated plan instead of `build_phase2_plan`) and `execute` (False = planned-only, no ToolCalls run).
- `POST /planner/jobs` now: generates plan → validates → on success creates a job that executes the EXACT validated LLM plan; added an `execute` flag (default False = planned, True = run). Response includes `plan_source` and `executed`.
- The runtime execution loop was unchanged — it already iterated `plan.steps` through Tool Registry + Adapter (`run_tool_call_job`). Only the plan *source* changed.
- MockLLMProvider's plan now references the conventional `ml_table` normalized object so the validated plan is executable end-to-end (no plan mutation/auto-repair by the bridge).
- Deterministic `build_phase2_plan` preserved as fallback: when no `analysis_plan` is provided, create_job uses it (Phase 2/3 product loop unchanged).
- **Key acceptance evidence**: `test_runtime_executes_exact_provided_plan_one_tool_call` proves a 1-step LLM plan produces EXACTLY 1 ToolCall (`ml.basic_metrics`, stepId `llm_step_1`), NOT the deterministic 5 ToolCalls. `test_runtime_deterministic_fallback_when_no_plan` proves fallback still works.
- Added `tests/test_phase8a_plan_execution.py` (11 tests). All execution still goes through Tool Registry + Adapter; unknown/V1/V2/invalid plans still rejected before job creation (Phase 7 validator unchanged).
- Baseline-freeze hardening added 4 tests covering exact-plan execution side effects: produces a `metrics_json` artifact, emits `tool.started`/`tool.completed`/`artifact.ready`/`plan.generated` events, job status reaches `completed`, and `execute=False` yields zero ToolCalls + no tool artifact + no tool events.
- Verification: backend 101 passed, 19 skipped, 0 failed; Phase 7 targeted 22 passed; frontend typecheck+build passed; uv lock + git diff clean.
- **Remaining boundary**: execution uses the in-memory `Phase2ProductRuntime` (synchronous local loop). Wiring the validated plan into the Redis `QueueWorkerRuntime` + PostgreSQL plan persistence is still future work (recorded in OPEN_QUESTIONS).

## 当前阶段

Phase 8A: LLM Plan Execution Bridge — **通过 (PASS) / baseline frozen**。validated LLM plan 现在真正执行（1-step → 恰好 1 ToolCall，非 deterministic 5），并验证了 Artifact/JobEvent/completed status 副作用 + execute=False 零 ToolCall。deterministic fallback 保留。backend 101 passed / 19 skipped / 0 failed。剩余边界：QueueWorkerRuntime + PostgreSQL plan persistence 待后续。

## 2026-06-27 Phase 7 LLM JSON Planner + BYOK Secret Management Update

- Implemented LLMPlannerProvider abstraction with 3 implementations:
  - MockLLMProvider: deterministic, no API key, returns valid AnalysisPlan for testing
  - OpenAICompatibleProvider: OpenAI/DeepSeek compatible with fake-transport support for testing
  - DeterministicPlannerAdapter: wraps existing build_phase2_plan() as fallback
- Added PlanValidator (strict mode, no auto-repair) in `packages/tool-registry/mdi_tool_registry/plan_validator.py`
  - Validates: JSON schema, step_id uniqueness, tool_id in ToolRegistry, MVP-only stage, no credentials in params, known artifact types, empty steps rejection, V1/V2 tool rejection
- Added planner prompt template in `services/llm/mdi_llm/planner_prompt.py` (JSON-only output, tool-aware system prompt)
- Added Planner API routes: POST /planner/preview, /planner/validate, /planner/jobs
  - /planner/preview: generates plan without creating job
  - /planner/validate: validates existing plan without creating job
  - /planner/jobs: plan → validate → create job (rejects invalid plans before job creation)
- Added SecretStore abstraction + InMemorySecretStore + EncryptedSecretStore placeholder
  - Secret list API never returns plaintext values
  - SecretStore creates/gets/deletes secrets internally
- Added secrets API routes: POST/GET/DELETE /me/secrets
- Added redaction helpers: credential key detection, secret value replacement in logs/params
- Added 19 Phase 7 tests: mock provider, schema validation, unknown tool rejection, V1/V2 rejection, duplicate step_id, empty steps, credential param rejection, preview no job, validate no job, plan→job flow, secret list no plaintext, secret CRUD, redaction, deterministic planner regression, OpenAI fake transport
- Security boundaries enforced:
  - LLM cannot execute Python/Shell, cannot bypass Tool Registry, cannot access secrets
  - Secret values never enter prompts, logs, JobEvents, Artifacts, Recipe, or Reports
  - params containing api_key/token/password are rejected at PlanValidator level
  - Preview and validate endpoints do not create jobs or enqueue work
- Verification: 87 passed, 19 skipped; frontend typecheck+build passed; git clean pending commit
- No real LLM key required for default pytest; MockLLMProvider + fake transport cover all test paths

## 2026-06-27 Phase 6B Live Integration Closeout Update

- GitHub Actions CI run [#28286885004](https://github.com/foolkking/material-data-intelligence/actions/runs/28286885004) completed with **full success**:
  - Unit Tests (Python 3.11): passed
  - Frontend Typecheck & Build: passed
  - Service-backed Integration (PostgreSQL + Redis + MinIO): **18 passed, 0 skipped, 0 failed**
- Alembic upgrade head ran against live PostgreSQL (CI service container) — 9 tables + 6 indexes verified
- MinIO bucket `mdi-artifacts` created and live-tested with put/get/exists/signed-url
- Redis queue live enqueue/handle tested against real Redis service container
- PostgreSQL repository live CRUD tested for all 9 entity types
- JobEvent seq monotonic/concurrent correctness verified on PostgreSQL with advisory lock strategy
- Service-backed product loop tested with real Tool Registry + BasicMetricsAdapter through execute_tool_request()
- CI workflow includes zero-skip enforcement: if any integration test skips, the job fails
- Added `httpx` to pyproject.toml dependencies (required by starlette.testclient)
- Fixed multiple P0 integration bugs: FK violations from shared project IDs, invalid job state transitions, ToolRegistry constructor mismatch
- **Final acceptance: PASS.** All 18 integration tests ran and passed on live Docker-backed PostgreSQL/Redis/MinIO via GitHub Actions. Phase 6 is live-verified.
- **Phase 6B closeout complete. Phase 7 may proceed.**

## 2026-06-26 Phase 6 Service-backed Runtime Smoke & Integration Hardening Update

- Re-read the required Phase 6 docs, Alembic baseline, persistent state, and docker-compose config before changes.
- Verified the Phase 5 baseline: clean Git status, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` all passed.
- Added 18 service-backed integration smoke tests in `tests/test_phase6_integration.py` covering:
  - Docker compose services reachability (PostgreSQL, Redis, MinIO).
  - Alembic live migration: real `alembic.command.upgrade(alembic_cfg, "head")` against PostgreSQL, plus downgrade+reupgrade cycle and index existence checks.
  - PostgreSQL repository live CRUD: Project, Dataset, Job, ToolCall, Artifact, Recipe, Report.
  - Transaction rollback and status transition rejection at repository boundary.
  - PostgreSQL JobEvent seq live: monotonic seq, advisory lock strategy, 30-event concurrent append correctness.
  - Redis queue live: enqueue/dequeue, QueueWorkerRuntime with PG repos + Redis backend.
  - Queue retry idempotency: duplicate job handle, crash+retry persistence.
  - MinIO live: put/get/exists/signed-url for json/text/bytes, signed URL structure validation.
  - Service-backed product-loop smoke: PG repos + Redis queue + MinIO storage + real Tool Registry + BasicMetricsAdapter (not fake executor).
- All 18 integration tests are gated with `@pytest.mark.integration` and skip cleanly when `MDI_RUN_INTEGRATION != 1` or Docker services are unreachable.
- Fixed `docker-compose.yml` MinIO healthcheck to use `mc ready local` for reliability.
- Updated `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` with integration test guide (sections 11-12), environment variables, category table, and troubleshooting for connection refused, migration failed, bucket not found, and signed URL invalid.
- Updated `.env.example` with `MDI_RUN_INTEGRATION` and `MDI_TEST_DATABASE_URL`.
- Verification:
  - `python -m pytest -q`: 68 passed, 19 skipped.
  - `python -m pytest tests/test_phase6_integration.py -q`: 18 skipped (Docker not available on this machine).
  - `python -m pytest -q -m integration`: all skipped (no Docker).
  - `uv lock --check`: passed.
  - `npm ci`: passed.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
- **Final acceptance**: CONDITIONAL PASS. Docker is not available on this machine; all 18 integration tests skip cleanly. Alembic test calls real `alembic.command.upgrade()`, service-backed loop test uses real Tool Registry + BasicMetricsAdapter, and git is clean at commit `e3c7a73`. Cannot enter Phase 7 until live Docker-backed integration is verified.

## 2026-06-26 Phase 5 PostgreSQL Runtime + Queue Worker + MinIO Integration Update

- Re-read the required Phase 5 project docs, Alembic baseline, and persistent state, then verified the Phase 4 baseline before changes: clean Git status, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` all passed.
- Added Phase 5 runtime configuration support for standard `DATABASE_URL`, `POSTGRES_*`, `REDIS_URL`, and `MINIO_*` variables while keeping existing `MDI_*` aliases.
- Added `mdi_api.database` engine/repository-factory helpers and made Alembic honor configured runtime database URLs while preserving the local SQLite fallback when no runtime DB env is set.
- Added `docs/16_RUNTIME_INFRASTRUCTURE_RUNBOOK.md` with Docker, Alembic, repository smoke, queue, MinIO, and integration-test operating notes.
- Extended `docker-compose.yml` and `.env.example` for one-command local infrastructure: PostgreSQL, Redis, and MinIO.
- Added live-capable `S3CompatibleArtifactStorage` behavior with optional boto3-compatible client support for `put_*`, `get_*`, `exists`, and real presigned URL generation; mapping/placeholder behavior remains unchanged when no client is configured.
- Added `QueueWorkerRuntime`, `InMemoryQueueBackend`, and `RedisRQQueueBackend`. The queue handler receives `job_id`, loads repository state, writes ToolCall status, JobEvents, Artifact metadata, and preserves idempotent retry behavior.
- Hardened SQLAlchemy JobEvent seq allocation for PostgreSQL with a transaction-scoped advisory lock keyed by `job_id`; SQLite/local tests continue to use the existing in-process lock.
- Verification:
  - `python -m pytest tests/test_phase5_runtime_infrastructure.py -q`: 7 passed, 1 skipped.
  - `python -m pytest -q`: 68 passed, 1 skipped, 50 third-party warnings.
  - `python -m pytest -q -m integration`: 1 skipped because external services were not enabled.
  - `uv lock --check`: passed.
  - `npm ci`: passed.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
  - `git diff --check`: passed with Windows line-ending notices only.

## 2026-06-26 Phase 4 Production Persistence Hardening Update

- Re-read the required project docs and persistent state, then verified the Phase 3 baseline before changes: clean Git status, `uv lock --check`, `python -m pytest -q`, `npm ci`, `npm run typecheck`, and `npm run build` all passed.
- Added an Alembic migration entrypoint and Phase 4 baseline revision for the PostgreSQL-oriented persistence schema while keeping SQLite-compatible SQLAlchemy metadata for tests.
- Hardened SQLAlchemy metadata for `jobs`, `tool_calls`, and `artifacts` with status checks, ToolCall idempotency fields, `(job_id, step_id)` uniqueness, artifact duplicate metadata detection, and storage-provider constraints.
- Added centralized `RepositorySession`, `UnitOfWork`, and `RepositoryFactory` transaction boundaries with rollback coverage.
- Added centralized Job/ToolCall status transition validation. The local synchronous worker keeps `created -> running` compatibility, while queued production flow can use `created -> queued -> running`.
- Added idempotent ToolCall and Artifact repository writes so repeated worker attempts reuse stable records instead of generating uncontrolled duplicates.
- Kept the Phase 2/3 product loop unchanged in scope: no real LLM, no V1/V2 tools, no Celery/Ray/Kubernetes, no production PostgreSQL runtime, no live MinIO/S3 client, and no frontend redesign.
- Verification after fixes:
  - `python -m pytest tests/test_phase4_persistence_hardening.py -q`: 8 passed.
  - `uv lock --check`: passed.
  - `python -m pytest -q`: 61 passed, 50 third-party warnings.
  - `npm ci`: passed.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
  - `git diff --check`: passed with Windows line-ending notices only.

## 2026-06-26 Phase 3 Acceptance Hardening Update

- Re-ran Phase 3 acceptance against the stricter handoff checklist: Phase 2 regression, repository coverage, database schema/indexes, JobEvent cursor semantics, SSE stream, ArtifactStorage mapping, API event/artifact routes, and reproducible frontend checks.
- Found and fixed P1 repository coverage gaps by adding `DataProfileRepository` and `ReportRepository` to both InMemory and SQLAlchemy repository bundles.
- Found and fixed a JobEvent cursor hardening gap by adding in-process append locks to the repository layer and `InMemoryJobStore`; tests now cover concurrent appends without duplicate seq values.
- Found and fixed P1 storage schema gaps by adding `storage_provider`, `bucket`, `content_type`, `sha256`, `size_bytes`, `preview_key`, and `created_at` metadata coverage across storage mapping, SQL metadata, migration draft, shared schemas, and artifact API summaries.
- Found and fixed a frontend P0 reproducibility issue where `npm run typecheck` depended on existing `.next/types`; added `apps/web/tsconfig.typecheck.json` so typecheck passes from a clean `.next` state.
- Kept scope unchanged: no real LLM, no V1/V2 tools, no Celery/Ray/Kubernetes, no production PostgreSQL/MinIO wiring, and no frontend feature expansion.
- Verification after fixes:
  - `npm ci`: passed.
  - `uv lock --check`: passed.
  - `python -m pytest -q`: 53 passed, 50 third-party deprecation warnings.
  - `npm run typecheck`: passed from a clean `.next` state.
  - `npm run build`: passed.

## 2026-06-26 Phase 3 Persistence Foundation Update

- Added Phase 3 persistence foundation without adding real LLM execution, V1/V2 tools, Celery/Ray/Kubernetes, full auth, or frontend expansion.
- Added repository abstraction for `ProjectRepository`, `DatasetRepository`, `JobRepository`, `JobEventRepository`, `ToolCallRepository`, `ArtifactRepository`, and `RecipeRepository`.
- Kept the Phase 2 local product loop on its InMemory path, while adding SQLAlchemy Core repositories that are SQLite-testable and PostgreSQL-oriented.
- Extended SQLAlchemy metadata and migration draft coverage for `projects`, `datasets`, `data_profiles`, `jobs`, `job_events`, `tool_calls`, `artifacts`, `visualization_recipes`, and `reports`.
- Added durable cursor semantics to job events: seq remains monotonic per job, `list_events_after_seq(job_id, after_seq)` exists, and `GET /jobs/{job_id}/events?after_seq=N` filters by cursor.
- Added `GET /jobs/{job_id}/stream` as an SSE smoke endpoint using the existing local runtime event stream.
- Added `ArtifactStorage` abstraction with local filesystem storage and an S3/MinIO-compatible mapping interface, including `storage_key`, `content_type`, `sha256`, `size_bytes`, and `preview_key` metadata.
- Added `GET /artifacts/{artifact_id}/download` as a local signed-url/download placeholder while preserving `GET /artifacts/{artifact_id}` for artifact detail.
- Added Phase 3 tests for repository interfaces, SQLAlchemy schema/cursor behavior, SSE smoke streaming, artifact storage mapping, and Phase 2 loop regression.
- Hardened frontend typecheck reproducibility by disabling stale incremental `tsconfig.tsbuildinfo` reuse in `npm run typecheck`.
- Verification:
  - `uv lock --check`: passed.
  - `python -m pytest -q`: 52 passed, 50 third-party deprecation warnings.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.

## 2026-06-25 Phase 2 Acceptance Hardening Update

- Re-ran the Phase 2 acceptance audit against the current worktree after the local product loop implementation.
- Fixed a shared-schema alignment issue in generated `AnalysisPlan.expectedArtifacts`: Phase 1 and Phase 2 planners now emit `{name, type, fromStepId}` entries instead of step-level grouped artifact summaries.
- Fixed Phase 2 job-level Recipe generation to include per-step `toolVersion` and `inputBindings` as `Record<string, string>`, matching `docs/13_SHARED_SCHEMA_SPEC.md` and `packages/schemas/src/index.ts`.
- Added shared Python/TypeScript schema types for `ExpectedArtifact` and `VisualizationRecipeStep`, and validated Phase 2 Recipe JSON with the Pydantic `VisualizationRecipe` model before export.
- Changed Phase 2 local-path uploads to parse the copied raw file under the runtime artifact root, keeping the accepted dataset path independent from the caller's original local path.
- Updated `docs/01_PRODUCT_REQUIREMENTS.md` and `README.md` to remove stale schema/status wording.
- Verification:
  - `python -m pytest -q`: 48 passed, 45 third-party deprecation warnings.
  - `npm ci`: passed from `apps/web/package-lock.json`.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
  - Manifest audit: 3 manifests load, registry version `0.1.0`, 10 MVP tools.
  - Phase 2 loop audit: project -> dataset upload -> profile -> plan -> job -> 5 tool calls -> 25 artifacts completed.
- Scope guard remains unchanged: no real LLM execution, no V1/V2 tool execution, no Celery/PostgreSQL/MinIO runtime persistence, and no frontend expansion this round.

## 2026-06-25 Phase 2 Local Product Loop Update

- Added `apps/api/mdi_api/phase2_runtime.py` as the Phase 2 in-memory product loop.
- The runtime now covers project creation, dataset upload from local paths or inline small files, deterministic parsing, `DataProfile` generation, deterministic `AnalysisPlan` generation, local Worker execution, Adapter invocation, Artifact export, JobEvent recording, job-level Recipe generation, Markdown/HTML report generation, and API result queries.
- Added Phase 2 API routes:
  - `POST /projects`
  - `POST /datasets/upload`
  - `GET /datasets/{dataset_id}/profile`
  - `POST /jobs`
  - `GET /jobs/{job_id}`
  - `GET /jobs/{job_id}/events`
  - `GET /jobs/{job_id}/tool-calls`
  - `GET /jobs/{job_id}/artifacts`
  - `GET /artifacts/{artifact_id}`
- The deterministic Phase 2 planner selects 3-5 MVP tools and currently chooses this five-tool mixed-dataset path when structures and an ML table are present:
  `composition.ptable_heatmap`, `composition.chem_sys_treemap`, `structure.viewer_3d`, `ml.basic_metrics`, and `ml.outlier_table`.
- Added `LocalFileArtifactStore` over `LocalArtifactExporter` output so API routes can return artifact metadata and text/JSON content without introducing MinIO.
- Kept execution inside the existing validated boundary:
  `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- Explicitly did not add real LLM API calls, full auth, V1/V2 tools, Celery, PostgreSQL, MinIO, or frontend feature expansion.
- Added `tests/test_phase2_product_loop.py` with coverage for data pipeline upload/profile, deterministic planner, local worker runtime, artifact store, API routes, and end-to-end product flow.
- Verification:
  - `python -m pytest -q`: 48 passed, 45 third-party deprecation warnings.
  - Frontend typecheck/build were not rerun because no frontend files changed in this Phase 2 implementation.
- `.gitignore` now ignores `material-data-intelligence-*.zip`, so the Phase 1 handoff archive can stay in the workspace without entering commits.

## 2026-06-25 Phase 1 Engineering Hardening Update

- Froze Python dependencies with `uv.lock`.
- Verified the Python test suite from an isolated uv-managed `.venv` using:
  `python -m pytest -q` -> 42 passed.
- Froze frontend dependencies with `apps/web/package-lock.json` because `pnpm` is not installed in the current environment.
- Verified frontend reproducibility from the lockfile with:
  - `npm ci`
  - `npm run typecheck`: passed
  - `npm run build`: passed
- Confirmed `.gitignore` covers generated dependency/build/cache outputs:
  `.venv/`, `*.egg-info/`, `node_modules/`, `.next/`, `.pytest_cache/`, `.pytest_tmp/`,
  `__pycache__/`, `*.pyc`, and `*.tsbuildinfo`.
- Phase 1 is now ready for a Git baseline commit and `git archive` handoff package after final cleanup.

## 2026-06-25 Phase 1 Product Acceptance Update

- Completed a docs/01 Phase 1 MVP acceptance pass against the current implementation.
- Added a deterministic Phase 1 product-flow runtime in `apps/api/mdi_api/phase1_demo.py`.
- The runtime covers: create project, parse upload set, Data Profile, natural-language request boundary, structured `AnalysisPlan`, registry-approved Worker execution, Artifact/Recipe generation, Markdown/HTML report, and JobEvent timeline.
- The demo flow validates all 10 MVP tools through Tool Registry + Adapter:
  `composition.ptable_heatmap`, `composition.elements_hist`, `composition.chem_sys_treemap`,
  `structure.structure_3d`, `structure.viewer_3d`, `structure.coordination_hist`,
  `ml.density_scatter`, `ml.error_distribution`, `ml.basic_metrics`, `ml.outlier_table`.
- Added API boundary routes for project creation, upload sessions, analysis requests, job events, event streaming, and artifact summaries.
- Expanded Phase 1 SQLAlchemy metadata to include the product-flow entities listed in docs/01: data profiles, field mappings, sessions/messages, jobs/events/tool calls/artifacts, recipes, configs, secrets, and audit logs.
- Updated the frontend shell so Agent Timeline, chart cards, 3D Viewer, Logs, Artifacts, Recipe, and Report surfaces are visible in the Phase 1 workspace.
- Verification passed:
  - `python -m pytest -q`: 42 passed, 25 third-party deprecation warnings.
  - `npm run typecheck`: passed.
  - `npm run build`: passed.
- Current Phase 1 caveats:
  - The product-flow runtime is deterministic/in-memory and intended for acceptance/demo, not a production repository or Celery deployment.
  - `preview_png` now has a minimal PNG fallback when Kaleido/Chromium is unavailable.
  - `structure.viewer_3d` may still emit a MatterViz-safe fallback HTML if widget rendering is unavailable.
  - Real object storage upload sessions, PostgreSQL repositories, Celery workers, and durable SSE cursors remain next-phase implementation work.

## 当前阶段

Phase 7: LLM JSON Planner + BYOK Secret Management — **通过 (PASS)**。90 passed, 19 skipped, 0 failed（22 个 Phase 7 tests + 68 个现有 tests）。MockLLMProvider + PlanValidator（严格，10 规则）+ SecretStore + Planner API 全部可测。**边界说明**：`/planner/jobs` 在 validate 成功后创建 job，但当前 job 实际运行的是 deterministic plan（`build_phase2_plan`），验证过的 LLM plan 尚未接入真实执行——「LLM→执行」闭环未打通，属已记录的后续工作（见 OPEN_QUESTIONS / ADR-075）。Secret 仅 InMemoryStore，生产 envelope encryption 未实现。

## 已完成阶段

- [x] Phase 0：项目目标与边界定义
- [x] Phase 1：产品需求与用户流程
- [x] Phase 2：总体系统架构
- [x] Phase 3：前端工作台设计
- [x] Phase 4：后端服务与数据库设计
- [x] Phase 5：Agent 编排设计
- [x] Phase 6：工具注册表与 Adapter
- [x] Phase 7：数据解析与 Data Profile
- [x] Phase 8：高并发任务系统
- [x] Phase 9：Artifact / Recipe / Report
- [x] Phase 10：用户配置、安全与扩展
- [x] Phase 11：MVP Roadmap

补充文件：

- [x] `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`：专业材料领域扩展设计
- [x] `docs/index.md`：文档索引
- [x] `docs/03A_FRONTEND_COMPONENT_SPEC.md`：前端组件规格
- [x] `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`：前端状态与交互规格
- [x] `docs/13_SHARED_SCHEMA_SPEC.md`：共享 Schema 基线
- [x] `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`：pymatviz 能力清单与平台 Tool ID 映射
- [x] `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`：Adapter 实现计划
- [x] `tool_registry/pymatviz_manifest.yaml`：pymatviz 原生能力 manifest
- [x] `tool_registry/matterviz_manifest.yaml`：MatterViz / widget 能力 manifest
- [x] `tool_registry/platform_builtin_manifest.yaml`：平台内置与自定义 Plotly 能力 manifest

当前新增设计重点：

本项目进一步明确为“以 pymatviz 为 primary visualization kernel 的材料数据智能分析与可视化平台”。当前补充了 pymatviz capability inventory、manifest-based tool registry 和 adapter implementation plan。

## 本轮完成

- 建立代码工程骨架：`apps/web`、`apps/api`、`services/workers`、`packages/schemas`、`packages/tool-registry`、`packages/adapters`、`packages/material-parsers`、`packages/artifact-core`、`tests/fixtures`。
- 新增根级 `pyproject.toml`，配置 Python 包发现、pytest 路径和核心材料依赖声明。
- 在 `packages/schemas` 中实现共享类型基线：
  - Python/Pydantic：`mdi_schemas.models`
  - JSON Schema：`packages/schemas/json/registered-tool.schema.json`
  - TypeScript 类型：`packages/schemas/src/index.ts`
- 在 `packages/tool-registry` 中实现 manifest loader：
  - `loadManifests()` / `load_manifests()`
  - `validateManifest()` / `validate_manifest()`
  - `getToolById()`、`listTools()`、`listToolsByStage()`、`listToolsByDomain()`、`listMvpTools()`
  - 校验 `tool_id` 唯一、`stage`、`implementation_source`、`display_target`、`artifact_types` 和 adapter class name。
- 在 `packages/artifact-core` 中实现本地文件系统 `LocalArtifactExporter`，输出稳定 storage key、content hash、Artifact metadata 和 provenance。
- 在 `packages/adapters` 中实现：
  - `BaseToolAdapter`
  - `ToolExecutionContext`
  - `ToolExecutionError` / error normalizer
  - Adapter class registry
  - Plotly export helper
- 实现 MVP 前 3 个 Adapter：
  - `composition.ptable_heatmap` -> `PTableHeatmapAdapter`
  - `structure.structure_3d` -> `Structure3DAdapter`
  - `structure.viewer_3d` -> `StructureViewer3DAdapter`
- 为 fixture 和测试补齐：
  - `tests/fixtures/structures/si.cif`
  - `tests/fixtures/tables/formulas.csv`
  - manifest loader、BaseToolAdapter、三个 Adapter、Artifact metadata/recipe 的最小测试。
- 真实环境核对并安装/升级运行依赖：`pymatviz 0.18.0`、`pymatgen 2026.5.4`、`ase 3.29.0`、`plotly 6.8.0`；为兼容 NumPy 2.x 同步升级 `xarray`、`pyarrow`、`numexpr`、`bottleneck`、`shapely`、`scikit-image`。
- 测试结果：`python -m pytest`，11 passed。
- 继续实现 Data Pipeline 最小库层：
  - 新增 `packages/material-parsers/mdi_material_parsers/detector.py`，支持 CIF、POSCAR/CONTCAR、CSV、JSON limited、ZIP、XYZ/EXTXYZ 的格式识别。
  - 新增 `packages/material-parsers/mdi_material_parsers/parsers.py`，支持 CIF/POSCAR -> `Structure`、CSV -> `DataFrame`、JSON limited -> `Structure` 或 simple table。
  - 新增 `packages/material-parsers/mdi_material_parsers/profile.py`，从 parse results 构建轻量 `DataProfile`、`structureSummary`、`tableSummary`、quality issues 和 recommended tasks。
  - 新增 normalized object draft 数据模型，记录 object id、object type、source file ids、storage key、metadata、hash 和 payload。
  - 补充 `tests/test_data_pipeline.py` 与 fixtures：`POSCAR`、`plain.xyz`、`ml_results.csv`。
  - 更新共享 `DataProfile` Pydantic model，补齐 `structureSummary`、`tableSummary`、`phononSummary`、`trajectorySummary` 可选字段。
  - 更新 `pyproject.toml`，显式加入 `pandas>=2.2`。
- 最新测试结果：`python -m pytest`，17 passed。
- 继续补齐剩余 7 个 MVP Adapter，并将 10 个 MVP 工具全部接入 adapter class registry：
  - `composition.elements_hist` -> `ElementsHistAdapter`
  - `composition.chem_sys_treemap` -> `ChemSysTreemapAdapter`
  - `structure.coordination_hist` -> `CoordinationHistAdapter`
  - `ml.density_scatter` -> `DensityScatterAdapter`
  - `ml.error_distribution` -> `ErrorDistributionAdapter`
  - `ml.basic_metrics` -> `BasicMetricsAdapter`
  - `ml.outlier_table` -> `OutlierTableAdapter`
- 新增 ML adapter 共用校验层，支持 DataFrame / records 输入、target/prediction 字段推断、数值列校验、metrics 和 outlier 计算。
- 新增测试覆盖全部 10 个 MVP Adapter，新增 manifest MVP adapter class registry 校验。
- 最新测试结果：`python -m pytest`，25 passed。
- 继续核验 Milestone 0/1 + 已实现库层闭环：
  - 将 pytest 临时目录固定到仓库内 `.pytest_tmp`，避免受限 sandbox 访问系统临时目录失败。
  - 将 plain XYZ Data Pipeline 语义对齐设计：解析为非周期 `Atoms` normalized object，并在 `DataProfile.qualityIssues` 中记录 `NON_PERIODIC_ATOMS` warning；它仍不会进入 `periodic_required` 的结构工具。
  - 新增 `.extxyz` 检测与 ASE->pymatgen 周期结构转换测试。
  - 新增 ZIP 安全解包回归测试，验证路径穿越 member 会被拒绝，保留 safe member 解析为 partial。
  - 新增 normalized object 稳定落盘 helper 测试，路径固定为 `projects/{project}/datasets/{dataset}/normalized/...`。
  - 最新测试结果：`python -m pytest`，25 passed。
- 继续核验共享 Schema 覆盖面：
  - 补齐 `packages/schemas/src/index.ts` 中的 TypeScript 核心类型导出：`JobStatus`、`JobEventStatus`、`ToolExecutionRequest`、`ToolCall`、`Artifact`、`AnalysisPlan`、`AnalysisStep`、`DataProfile`、`VisualizationRecipe` 等。
  - 在 Python/Pydantic schema 中新增 `JobEvent`，为后续 SSE / Agent Timeline 事件流复用同一共享类型。
  - 新增 `tests/test_shared_schemas.py`，校验 Python 和 TypeScript schema 入口暴露用户要求的核心类型。
  - 最新测试结果：`python -m pytest -q`，30 passed，20 warnings；warnings 来自当前 Anaconda 环境中的 matplotlib/Jupyter/ipywidgets 依赖弃用提示，不影响本阶段功能。
- 继续补齐受控执行库层入口：
  - 新增 `packages/adapters/mdi_adapters/executor.py`，提供 `execute_tool_request()`，执行顺序为 Tool Registry lookup -> input resolution / cache key -> paramsSchema validation -> optional in-memory cache lookup -> adapter instantiation -> adapter execution。
  - 新增 `ToolExecutionResult`，记录 `tool`、`artifacts`、`cache_key`、`cache_hit`，为后续 ToolCall 状态表和 JobEvent 持久化留出结构化结果。
  - 新增 `tests/test_tool_executor.py`，覆盖 registry 路由、非法参数拒绝、未注册 tool 拒绝和 cache hit。
  - 最新测试结果：`python -m pytest -q`，34 passed，20 warnings；warnings 仍为当前 Anaconda 第三方依赖弃用提示。
- 继续补齐 Worker 语义基线：
  - 新增 `services/workers/mdi_workers/runtime.py`，提供 `run_tool_call_job()` 和开发用 `InMemoryJobStore`。
  - `run_tool_call_job()` 会记录 Job status、ToolCall status、`tool.started`、`artifact.ready`、`tool.completed` / `tool.failed` JobEvent，并保留事件 `seq` 单调递增语义。
  - ToolCall 记录会对 secret-like params 做脱敏，失败路径不会保存明文 API key / BYOK。
  - 新增 `tests/test_worker_runtime.py`，覆盖成功事件流和失败脱敏路径。
  - 最新测试结果：`python -m pytest -q`，36 passed，20 warnings；warnings 仍为当前 Anaconda 第三方依赖弃用提示。
- 本轮恢复核验：
  - 已按新会话要求重新读取 `README.md`、`AGENTS.md`、`MASTER_PROMPT.md`、核心 `docs/`、3 个 manifest 和 `persistent/` 状态文件。
  - 已检查 `git status --short`，确认上一轮代码与文档仍处于未提交工作区中；本轮继续在该状态上增量推进，未回退既有变更。
  - 已检查配置，当前仅存在 Python `pyproject.toml` 测试配置，未发现前端 `package.json` / `pnpm-workspace.yaml`。
  - 已运行基线测试：`python -m pytest -q`，36 passed，20 warnings。
- 本轮补强 Tool Registry paramsSchema：
  - 将剩余 MVP 工具的 `paramsSchema` 从宽松 `additionalProperties: true` 收紧为平台批准参数白名单：
    `composition.elements_hist`、`composition.chem_sys_treemap`、`structure.coordination_hist`、`ml.density_scatter`、`ml.error_distribution`、`ml.basic_metrics`、`ml.outlier_table`。
  - 新增 `tests/test_manifest_loader.py::test_mvp_tools_reject_unregistered_params`，确保 10 个 MVP 工具均拒绝未注册参数。
  - 最新测试结果：`python -m pytest -q`，37 passed，20 warnings；warnings 仍为当前 Anaconda 第三方依赖弃用提示。
- 本轮完成 Milestone 1 scaffold：
  - 新增 `docker-compose.yml`，配置本地 PostgreSQL、Redis、MinIO 服务；新增 `.env.example` 并只保留占位符，不写入真实 Secret。
  - 新增 `apps/api/mdi_api` FastAPI app factory、配置加载、模块路由边界和 SQLAlchemy Core metadata。
  - 建立基础 Auth / Project / Dataset 表元数据：`users`、`organizations`、`projects`、`project_members`、`datasets`、`files`。
  - 新增 `/health`、`/auth/me`、`/projects`、`/datasets`、`/tools`、`/tools/mvp` API 边界，其中工具路由读取 Tool Registry。
  - 新增 `apps/web` Next.js App Router shell、三栏式工作台页面、底部面板、`package.json`、`tsconfig.json`、`next.config.mjs` 和 `pnpm-workspace.yaml`。
  - 更新 `pyproject.toml`，纳入 `apps/api` 包发现和 `fastapi`、`sqlalchemy`、`uvicorn`、`starlette>=0.40,<0.47` 依赖边界。
  - 修正当前 Anaconda 环境中 `starlette 1.0.0` 与 `fastapi 0.115.12` 不兼容的问题，将 Starlette 降级到 `0.46.2`。
  - 新增 `tests/test_phase1_scaffold.py`，验证 API route 边界、数据库表元数据、compose 服务和前端 shell 文件。
  - 最新测试结果：`python -m pytest -q`，41 passed，20 warnings；`npm run typecheck` passed；`npm run build` passed。

- 创建 `docs/00_PROJECT_GOAL.md`。
- 创建 `persistent/PROJECT_BRIEF.md`。
- 初始化持久化跟踪文件。
- 明确系统是材料数据智能分析与可视化平台，而不是 pymatviz 套壳。
- 明确 LLM 采用 JSON Plan + Tool Registry 的受控执行模式。
- 明确 MVP 优先覆盖文件上传、格式识别、Data Profile、Agent Plan、白名单工具调用、Artifact、Recipe 和报告基础链路。
- 补充独立系统定位：自然语言 + 材料数据文件 -> Plotly / MatterViz 图表、3D 模型、过程展示和可复现 Artifact。
- 补充 pymatviz / MatterViz 数据输入、可视化能力、3D 渲染路线和 MVP 工具集。
- 补充 Adapter 层决策：不 fork 大改 pymatviz，通过 Tool Registry 和 Visualization Service 隔离上游变化。
- 创建 `docs/01_PRODUCT_REQUIREMENTS.md`。
- 完成用户角色、用户故事、上传流程、Data Profile 流程、自然语言分析流程、图表生成流程、3D 模型查看流程、Agent Timeline、Artifact / Recipe / Report 流程定义。
- 明确 Phase 1 产品决策：MVP 仅登录用户、默认 Auto 模式、用户审查计划摘要但不编辑 JSON Plan、报告导出支持 Markdown/HTML。
- 创建 `docs/02_SYSTEM_ARCHITECTURE.md`。
- 明确 MVP 架构：Next.js 前端 + FastAPI 模块化应用 + Celery/Redis Worker + PostgreSQL + S3/MinIO。
- 明确逻辑服务边界：API Gateway、Data Service、Agent Service、Visualization Service、Worker Service、Artifact Service、Storage Layer、Queue Layer、Security Layer。
- 明确所有耗时任务必须通过 Job Queue 异步执行，前端通过 SSE/WebSocket 渐进展示 JobEvent。
- 创建 `docs/03_FRONTEND_WORKSPACE_DESIGN.md`。
- 明确前端采用三栏式工作台 + 底部面板：左侧数据资产、中央可视化画布、右侧 Agent 面板、底部 Logs/Code/Artifacts/Recipe/Warnings。
- 明确 MVP 使用固定响应式 Dashboard，MatterViz / heavy Plotly 优先通过 sandboxed artifact iframe 展示。
- 明确 Agent Plan 默认展示摘要，完整 JSON 和 ToolCall 细节可展开。
- 创建 `docs/04_BACKEND_SERVICE_DESIGN.md`。
- 明确后端模块边界：Auth、Project、Dataset、Profile、Jobs、Agent、Tools、Artifacts、Config、Secrets、Audit、Workers。
- 明确 MVP 上传采用对象存储预签名直传，不做分片/断点续传。
- 明确核心数据库实体、项目级 RBAC、数据隔离、统一错误模型和审计日志边界。
- 创建 `docs/05_AGENT_ORCHESTRATION_DESIGN.md`。
- 明确 Agent 职责：Intent Parser、Data-aware Planner、Tool Selector、Parameter Generator、Result Explainer、Report Writer。
- 明确 Agent 只能输出 JSON Analysis Plan，Execution Controller 校验后创建 ToolCall。
- 明确 MVP 不做自动多模型路由和完整工具文档 RAG；使用项目默认模型和静态 Tool Registry 摘要。
- 明确 Prompt injection 进入 Agent Timeline warning，并可阻止高风险计划执行。
- 创建 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md`。
- 明确 Tool Registry 是唯一执行白名单，Adapter 隔离 pymatviz / MatterViz / Plotly 上游变化。
- 明确 MVP Tool Set、Tool Schema、Artifact 标准、ToolError、缓存 key 和插件扩展机制。
- 明确 MVP Phonon 工具推迟到 V1，当前只保留 Schema 和扩展点。
- 创建 `docs/07_DATA_PIPELINE_DESIGN.md`。
- 明确数据管线流程：格式识别、安全解析、标准化对象、Data Profile、质量检查、推荐任务。
- 明确 MVP 支持 CIF、POSCAR/CONTCAR、XYZ/EXTXYZ 基础解析、CSV、JSON、ZIP；phonon/trajectory 深度支持推迟到 V1，VASP/LAMMPS 推迟到 V2。
- 明确代表 3D 结构 MVP 采用规则采样，composition clustering 推迟到 V1。
- 创建 `docs/08_JOB_QUEUE_AND_CONCURRENCY.md`。
- 明确 MVP 使用 SSE 推送 JobEvent，WebSocket 协作能力推迟到 V1。
- 明确 Worker 按 parse/profile/llm/viz/render/export 队列拆分。
- 明确 PostgreSQL 是 Job/ToolCall/Artifact 状态事实源，Redis 只做 broker/cache/短期状态。
- 明确大数据降采样、3D LOD、资源限制、多用户并发和可观测性策略。
- 创建 `docs/09_ARTIFACT_AND_RECIPE_SYSTEM.md`。
- 明确 Plotly `figure.json`、MatterViz `viewer.html + metadata.json`、Report Markdown、Recipe JSON 的 canonical 地位。
- 明确 Artifact / Recipe / Report 默认不可变，重跑或编辑生成新 version。
- 明确 MVP 不支持公开分享，只支持项目成员访问和授权导出包。
- 创建 `docs/10_USER_CONFIG_AND_SECURITY.md`。
- 明确配置优先级：system defaults < user_config < project_config < recipe/job params。
- 明确 MVP 使用 Docker/容器化 Worker 沙箱，用户级 BYOK，组织级共享 Key 推迟到 V1。
- 明确 Secret envelope encryption、文件安全、Prompt injection MVP 防护、审计日志和插件默认最小权限。
- 创建 `docs/12_MVP_ROADMAP.md`。
- 明确 MVP / V1 / V2 范围、技术栈、开发里程碑、优先级、风险清单、验收标准和进入代码实现顺序。
- Phase 0-11 设计文档全部完成。
- 复核用户给定目标文件清单，补充创建 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 修正 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md` 中 phonon / trajectory 工具阶段归属，使其与 ADR 和 Roadmap 一致：V1 支持 phonon band/DOS 与 trajectory viewer，V2 支持 VASP/LAMMPS、电子结构、生成材料评估和外部生态插件。
- 更新 `docs/12_MVP_ROADMAP.md` 的设计完成标准，纳入 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md`。
- 完成逐文件审核，创建 `docs/index.md` 作为文档入口。
- 修正 `docs/01_PRODUCT_REQUIREMENTS.md` 中 MVP 示例混入 V1 `structure.spacegroup_bar` 的表述。
- 修正 `docs/03_FRONTEND_WORKSPACE_DESIGN.md` 中 TrajectoryWidget MVP 表述，明确 MVP 仅基于已解析结构集合展示首末帧/抽样帧，不提供完整 trajectory 工具。
- 更新 `persistent/TOOL_REGISTRY_NOTES.md`，补齐 `ml.parity_plot` 的 V1 归属，并区分 V1 phonon/trajectory 与 V2 VASP/LAMMPS。
- 完成 Design Review Fixes：修正 `.gitignore`，确保 `docs/` 和 `persistent/` 进入 Git 版本管理。
- 新增根目录 `README.md`、`AGENTS.md`、`MASTER_PROMPT.md`，作为新会话和 Coding Agent 入口。
- 新增 `docs/13_SHARED_SCHEMA_SPEC.md`，统一 `ArtifactType`、`DisplayTarget`、`ToolCategory`、`ToolDomain`、`ToolInputSchema`、`AnalysisPlan`、`JobEvent`、`Recipe`、`Config` 等跨模块 Schema。
- 新增 `docs/03A_FRONTEND_COMPONENT_SPEC.md` 和 `docs/03B_FRONTEND_STATE_AND_INTERACTION.md`，补齐前端组件树、状态切片、Artifact Loader、全屏/重试/错误态和 SSE 事件投影。
- 统一 MVP/V1 工具范围：MVP 为 composition/structure/ml 的 10 个核心工具；V1 扩展 parity、uncertainty、error-by-domain、phonon、trajectory、RDF/XRD、composition clustering。
- 修正 Tool Registry：`ToolInputSchema` 改为 `inputOptions` 多输入方案，增加 `implementationSource`、`ToolDomain` 和周期性结构约束。
- 增加 `metrics_json`、`table_json`、`table_csv`、`quality_issues_json`，将指标和表格结果作为一等 Artifact。
- 修正 JSON limited、ZIP 容器、plain XYZ / EXTXYZ 与周期结构工具的边界。
- 调整 MatterViz snapshot、SVG/PDF high-resolution export 的阶段归属，MVP 不把这些作为阻塞项。
- 明确 BYOK 多人项目规则：用户级 Secret 按 job runner 解析，Recipe 不保存具体 SecretRef。
- 补充 JobEvent 关键数据库索引和事件/日志保留策略。
- 更新 ADR-027、ADR-042，并新增 ADR-048 至 ADR-057。
- 完成第二轮实现前一致性修正：补全 `docs/13_SHARED_SCHEMA_SPEC.md` 中 `FileProfile`、`ObjectProfile`、`QualityIssue`、`RecommendedTask`、`InputRef`、`ToolExecutionRequest` 和 `Molecule`。
- 统一 `artifactTypes` 命名，移除旧的 format 语义残留。
- 删除 Phase 0 旧 Schema 草案，改为引用 `docs/13_SHARED_SCHEMA_SPEC.md`。
- 修正 Phase 3 `activeTab` 为 `DisplayTarget`，修正 Phase 4 `job_events.seq`，修正 Phase 12 10 个 MVP 工具与 Milestone 3 的冲突。
- 将推荐任务增加 `stage`、`availableNow`、`requiredTools` 和 `reason` 语义，避免 MVP Planner 自动选择 V1 工具。
- 统一 Redis 只作为 broker/cache/transient state 的表述；Celery result backend 若启用也不作为业务事实源。
- 在 `README.md` 增加对外分享压缩包排除 `.git/` 的建议。
- 完成第三轮一致性修正：统一 JobEvent status 为 `info/running/success/warning/error`，移除 retry 专用 JobStatus，修正用户配置导出格式为 download format，确认 Phase 0 只引用共享 Schema，确认 Tool Registry 执行流和 Markdown 代码块无重复/破损。
- 完成第四轮实现前一致性修正：拆分 MVP 10 个工具实现标准与 6 个工具端到端演示标准；统一 Plotly MVP 交互展示产物口径；Phase 2 `JobEvent` 补齐 `seq/progress` 并让 `ArtifactRecord` 引用共享 `Artifact`；Phase 4 表字段补齐索引依赖的时间字段；MVP Secret API 改为用户级 `/me/secrets`，项目级共享 Secret 推迟到 V1；Agent Timeline 状态与共享 `JobEvent.status` 对齐。
- 完成第五轮实现前小修：Phase 1 MVP 验收标准与 Phase 12 完全对齐；Phase 1 上传范围补齐 POSCAR/CONTCAR、JSON limited、XYZ/EXTXYZ 基础解析；Phase 6 / Phase 9 Artifact 元数据改为引用 `docs/13_SHARED_SCHEMA_SPEC.md` 的正式 `Artifact` / `ArtifactMetadata`；复核 Phase 6 缓存策略中 `refresh` 条目无重复。
- 完成 pymatviz 能力抽象基线补充：新增 `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md`，明确 Level 0-5 能力分层、9 类 pymatviz/MatterViz/Plotly 能力、原始函数到平台 Tool ID 的映射表，以及 3 个 MVP capability 完整示例。
- 新增 `tool_registry/pymatviz_manifest.yaml`、`tool_registry/matterviz_manifest.yaml`、`tool_registry/platform_builtin_manifest.yaml`，将 10 个 MVP 工具来源拆分为 pymatviz、MatterViz、plotly_custom 和 platform_builtin。
- 新增 `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md`，明确 BaseToolAdapter 接口、执行流程、MVP Adapter 实现顺序和测试要求。
- 更新 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md` 与 `docs/12_MVP_ROADMAP.md`，把 manifest-based Tool Registry 和 Milestone 0 纳入正式实现顺序。

## 当前阻塞

无架构方向阻塞。Milestone 1 scaffold 已完成：本地 infra 配置、FastAPI API 边界、基础 Auth/Project/Dataset 表元数据和 Next.js 工作台 shell 均已有测试或构建证据。当前仍有工程化后续项：建议建立隔离虚拟环境/锁文件，避免继续修改全局 Anaconda 环境；`preview_png` 因 Kaleido/Chromium 依赖仍按 MVP optional 处理；ZIP 解包已具备最小安全解析但仍需补更多安全测试；EXTXYZ with lattice 需要继续验证；当前 Worker runtime 仍是内存语义基线，尚未接入 Celery / PostgreSQL / SSE。

## 下一步

下一步按 Roadmap 继续进入 Milestone 2 / Milestone 4 的交界：建立隔离依赖/锁文件，补齐 parser artifact storage、上传/对象存储边界、更多 ZIP / EXTXYZ 回归测试；随后接 Celery Job Queue、PostgreSQL ToolCall/Artifact 状态持久化和 SSE 事件流。
## 2026-07-04 Phase 9B Official pymatviz Examples Evidence Pack

- Generated a global evidence pack for `C:\Users\86182\Desktop\pymatviz_official_examples_test_suite`.
- Audited all 61 manifest cases and wrote `GLOBAL_CASE_AUDIT.md`.
- Updated `OFFICIAL_BROWSER_VERIFICATION_SUMMARY.md` with honest verdicts:
  - 22 `PASS_WITH_CURRENT_PLATFORM_SCOPE`
  - 30 `PARTIAL_PASS`
  - 9 `FUTURE_SCOPE`
- Browser-verified the two direct-uploadable cases with Mock Planner only:
  - `matpes_atomic_energies_csv`
  - `ward_metallic_glasses_csv_xz`
- Both direct cases now have real upload/profile/job/event/tool-call/artifact/result API evidence, downloaded artifact files, and 4 required browser screenshots.
- Current direct evidence scope is metrics only: persisted AnalysisPlan -> `ml.basic_metrics` -> `metrics_json` artifact -> system-generated report/recipe summary.
- Official richer outputs such as histograms, composition plots, classification plots, phonon, Brillouin zone, and advanced widgets are preserved under `future_expected_*`; they are not claimed as completed.
- Platform fixes made during evidence repair:
  - CSV parser now coerces numeric-looking string columns when safe.
  - Mock Planner now ignores sparse `Unnamed:` columns for metrics selection and uses DataProfile numeric columns instead of hard-coded `y_true/y_pred`.
- True LLM was not used. This remains Mock Planner demo evidence, not live LLM verification.

## 2026-07-06 Phase 10B-1 Composition Visualization Adapter Implementation

- Implemented the second-batch composition visualization adapter set:
  - `composition.formula_statistics`
  - `composition.elements_hist`
  - `composition.ptable_heatmap`
  - `composition.chem_sys_treemap`
  - `composition.chem_sys_sunburst`
- Added shared deterministic composition parsing/statistics helpers for formula column detection, pymatgen-backed parsing, partial-failure warnings, element counts, chemical systems, arity labels, Plotly metadata, summaries, and recipes.
- Registered all five tools through the Tool Registry and adapter registry. Execution remains Tool Registry -> params schema -> adapter -> artifact exporter.
- Updated Mock Planner routing so explicit composition prompts route before generic histogram/correlation/table routing.
- Generated lightweight Ward official-example adapter evidence under `docs/phase10b/adapter_evidence/`.
- This phase did not run real LLM, did not create browser/API evidence, and did not modify QueueWorkerRuntime, AnalysisPlanRepository, or `/planner/jobs` semantics.
- Remaining next step: Phase 10B-2 browser/API/artifact evidence for these composition adapters.

## 2026-07-06 Phase 10B-2 Browser/API Evidence for Composition Visualization Adapters

- Generated end-to-end browser/API/artifact evidence for the five Phase 10B-1 composition adapters under `docs/phase10b/browser_api_evidence/`.
- Verified Ward direct-uploadable composition workflows through Phase 9C UI, Mock Planner, persisted AnalysisPlan, queue worker execution, Tool Registry, adapters, artifacts, reports, and recipes.
- Covered:
  - `ward_formula_statistics` -> `composition.formula_statistics`
  - `ward_elements_hist` -> `composition.elements_hist`
  - `ward_ptable_heatmap` -> `composition.ptable_heatmap`
  - `ward_chem_sys_treemap` -> `composition.chem_sys_treemap`
  - `ward_chem_sys_sunburst` -> `composition.chem_sys_sunburst`
- Evidence totals: 50 redacted API captures, 25 browser screenshots, 19 artifact files, and 5 evidence manifests.
- Security scan result: `NO_SECRET_PATTERN_HITS`.
- Made one evidence-contract fix: `composition.ptable_heatmap` now emits `ptable_heatmap.json` instead of a generic `figure.json`, matching the Phase 10B-1/10B-2 artifact contract.
- No real LLM was used, and default CI remains gated away from live LLM calls.
- QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, and PlanValidator semantics were not changed.
- Remaining work: Phase 10C lightweight structure planning, structure viewer polish, XRD, RDF, phonon, Brillouin zone, and notebook/script extraction.

## 2026-07-07 Phase 10C-2 Browser/API Evidence for Lightweight Structure Adapters

- Generated end-to-end browser/API/artifact evidence for the five Phase 10C-1 lightweight structure adapters under `docs/phase10c/browser_api_evidence/`.
- Verified simple cubic structure workflows through Phase 9C UI, Mock Planner, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry, adapters, artifacts, reports, and recipes.
- Covered:
  - `simple_cubic_structure_summary` -> `structure.summary`
  - `simple_cubic_lattice_summary` -> `structure.lattice_summary`
  - `simple_cubic_spacegroup_summary` -> `structure.spacegroup_summary`
  - `simple_cubic_composition_from_structure` -> `structure.composition_from_structure`
  - `simple_cubic_preview_metadata` -> `structure.preview_metadata`
- Evidence totals: 45 redacted API captures, 25 browser screenshots, 15 artifact files, and 5 evidence manifests.
- Security scan result: `NO_SECRET_PATTERN_HITS`.
- Spacegroup evidence used the actual available symmetry path and did not fabricate fallback symmetry.
- No real LLM was used, and default CI remains gated away from live LLM calls.
- QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, and existing Phase 10A/10B adapter semantics were not changed.
- Remaining work: Phase 10D advanced structure visualization planning, 3D viewer, XRD, RDF, coordination histogram, phonon, Brillouin zone, and notebook/script extraction.

## 2026-07-07 Phase 10D Advanced Structure Visualization Planning

- Added Phase 10D planning docs under `docs/phase10d/`.
- Current confirmed structure baseline is Phase 10C-2: lightweight structure browser/API/artifact evidence is complete at commit `a20afb3`.
- Defined a four-layer advanced structure roadmap:
  - Layer 1: viewer scene metadata and static export package.
  - Layer 2: static physics plots such as XRD, RDF, and coordination histogram.
  - Layer 3: interactive 3D viewer and Brillouin-zone 3D.
  - Layer 4: phonon bands, DOS, and combined band/DOS.
- Recommended Phase 10D-1 scope is `structure.viewer_scene_metadata` and `structure.viewer_export_package`, with optional schema-only `structure.viewer_3d_contract`.
- Explicitly deferred full interactive `structure.viewer_3d`, WebGL renderer work, Brillouin-zone 3D, XRD/RDF implementation, phonon tools, notebook extraction, and script execution.
- No adapter, Tool Registry, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, or PlanValidator implementation was changed in this planning phase.

## 2026-07-07 Phase 10D-1 Viewer Scene Metadata / Export Package Implementation

- Implemented `structure.viewer_scene_metadata` and `structure.viewer_export_package`.
- Did not implement optional `structure.viewer_3d_contract`; the current contract is carried by `viewer_scene.json`.
- Added deterministic static artifacts: `viewer_scene.json`, `viewer_assets_manifest.json`, `summary.md`, and `recipe.json`.
- Registered both tools through Tool Registry with strict params validation and structure resource limits.
- Added Mock Planner routing for viewer scene metadata and static export package prompts.
- Full interactive `structure.viewer_3d`, WebGL renderer, Brillouin-zone 3D, XRD, RDF, coordination histogram, phonon tools, notebook extraction, and script execution remain deferred.
- Browser/API evidence is deferred to Phase 10D-2; Phase 10D-1 evidence is adapter-level only under `docs/phase10d/adapter_evidence/`.
- QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, and the default real-LLM gate were not changed.

## 2026-07-08 Phase 10D-2 Browser/API Evidence for Viewer Scene Metadata

- Generated Browser/API/artifact evidence for the Phase 10D-1 static viewer metadata tools under `docs/phase10d/browser_api_evidence/`.
- Covered both registered tools:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- Covered three lightweight input forms: small CIF, small POSCAR, and generated pymatgen Structure JSON.
- Evidence totals: 99 redacted API captures, 30 browser-rendered static preview screenshots, 21 artifact files, and 6 case manifests.
- Verified each case through upload/profile, Mock Planner preview, PlanValidator, persisted AnalysisPlan, `/planner/jobs`, QueueWorkerRuntime, Tool Registry, Adapter execution, artifact generation, result readback, and static artifact preview.
- Security scan result: `NO_SECRET_PATTERN_HITS`.
- Artifacts remain static JSON/Markdown only: `viewer_scene.json`, `viewer_assets_manifest.json`, `summary.md`, and `recipe.json`.
- No real LLM was used, and default CI remains gated away from live LLM calls.
- QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, Phase 10A/10B/10C adapters, and the Phase 10D-1 artifact contract were not changed.
- Full interactive `structure.viewer_3d`, WebGL renderer, Brillouin-zone 3D, XRD, RDF, coordination histogram, phonon tools, notebook extraction, script execution, and unsupported official example claims remain deferred.

## 2026-07-08 Phase 10D-3 Viewer Static Preview Hardening

- Hardened the frontend artifact preview for static viewer metadata/export package artifacts.
- Added schema-aware static preview coverage for `viewer_scene.json`, including scene overview, lattice, atoms, bonds, display/camera metadata, limits, warnings, security badges, and raw JSON fallback.
- Added schema-aware static preview coverage for `viewer_assets_manifest.json`, including package overview, artifact list, renderer status, limits, warnings, security badges, and raw JSON fallback.
- Hardened `summary.md` and `recipe.json` previews so static text, deterministic recipe fields, steps, and raw JSON fallback are visible.
- Added browser-rendered Phase 10D-3 static preview evidence under `docs/phase10d/browser_api_evidence/phase10d3_static_preview_hardening/`.
- Evidence totals for this hardening phase: 10 browser-rendered static preview screenshots and 10 committed static browser pages; no new API captures because Phase 10D-2 already covered the API path.
- No new adapter was added, no Tool Registry semantics changed, and QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, and the Phase 10D-1 artifact contract were not changed.
- Full interactive `structure.viewer_3d`, WebGL renderer, Three.js, canvas-based rendering, Brillouin-zone 3D, XRD, RDF, coordination histogram, phonon tools, notebook extraction, script execution, and unsupported official example claims remain deferred.

## 2026-07-08 Phase 10E Static Structure Physics Plot Planning

- Added Phase 10E planning docs under `docs/phase10e/`.
- Planned static structure physics candidates:
  - `structure.xrd`
  - `structure.rdf`
  - `structure.coordination_hist`
- Dependency check found `pymatgen`, `pymatviz`, `numpy`, `scipy`, `matplotlib`, `plotly`, and `spglib` available, but Phase 10E does not add dependencies.
- Recommended Phase 10E-1 first target is `structure.coordination_hist` with a conservative deterministic distance-cutoff neighbor policy.
- `structure.xrd` is the second candidate if XRD fixture peak windows and tolerances are pinned before implementation.
- `structure.rdf` remains deferred until normalization, cutoff, binning, and periodic-boundary policies are fixed.
- Official examples for XRD/RDF are future-scope widget/script mappings, not direct-uploadable PASS evidence.
- No adapter, Tool Registry, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, frontend runtime, browser/API evidence, or real LLM path was changed.
- Full interactive `structure.viewer_3d`, WebGL renderer, Brillouin-zone 3D, phonon tools, trajectory RDF, experimental XRD fitting, notebook extraction, script execution, and external API workflows remain deferred.

## 2026-07-08 Phase 10E-1 Coordination Histogram Implementation

- Implemented `structure.coordination_hist` as the first low-risk static physics adapter.
- The adapter uses a deterministic `distance_cutoff` neighbor policy with strict params validation.
- Generated deterministic artifacts: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json`.
- Registered the tool through Tool Registry and added Mock Planner routing for coordination histogram prompts.
- Added adapter, fixture, registry, planner routing, artifact contract, security, and persisted execution tests.
- Browser/API evidence remains deferred to Phase 10E-2.
- No XRD, RDF, full interactive 3D viewer, WebGL renderer, Brillouin-zone 3D, phonon, notebook/script extraction, external API workflow, or advanced local environment classification was implemented.

## 2026-07-08 Phase 10E-2 Coordination Histogram Browser/API Evidence

- Added Browser/API/artifact evidence for `structure.coordination_hist` under `docs/phase10e/browser_api_evidence/phase10e2_coordination_hist/`.
- Covered three bounded structure inputs: small CIF, small POSCAR, and generated pymatgen Structure JSON.
- Evidence totals: 43 redacted API captures, 6 browser-rendered static preview screenshots, and 12 artifact capture files.
- Verified API/job flow through Mock Planner, PlanValidator, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry, adapter execution, artifact generation, result readback, and static browser preview.
- Verified artifacts: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json`.
- Security scan result: `NO_SECRET_PATTERN_HITS`; artifact scan found no script, JavaScript URL, external URL, CDN, Three.js, or eval patterns.
- Negative routing evidence confirms XRD, RDF, full 3D viewer, WebGL, Brillouin-zone, phonon, Voronoi, and CrystalNN prompts do not route to `structure.coordination_hist`.
- No new adapter was implemented, and no runtime main semantics or Phase 10E-1 coordination policy were changed.

## 2026-07-08 Phase 10E-3 XRD / RDF Readiness Decision

- Added Phase 10E-3 readiness docs under `docs/phase10e/`.
- Confirmed `structure.coordination_hist` implementation and browser/API evidence are the current static physics baseline.
- Assessed `structure.xrd` and `structure.rdf` across dependency, fixture, determinism, tolerance, artifact contract, routing, evidence, CI, security, and official-example readiness gates.
- Local dependency check confirms `pymatgen`, `pymatviz`, `numpy`, `scipy`, `plotly`, `spglib`, `ase`, and `pymatgen.analysis.diffraction.xrd.XRDCalculator` are available without adding dependencies.
- Decision: recommend Phase 10E-4 implement `structure.xrd` only.
- Rationale: XRD has available dependencies, small crystalline fixtures, clear static JSON/chart artifact contracts, and manageable tolerance pinning work.
- RDF remains deferred because normalization, cutoff/binning, periodic-image handling, finite-size warnings, and partial-pair policy are not ready.
- Official examples remain mapping references only; no XRD/RDF official example is claimed as PASS evidence.
- No adapter, Tool Registry, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, PlanValidator, frontend runtime, browser/API evidence, or real LLM path was changed.
- Full interactive `structure.viewer_3d`, WebGL renderer, Brillouin-zone 3D, phonon tools, notebook extraction, script execution, and external API workflows remain deferred.

## 2026-07-08 Phase 10E-4 XRD Implementation

- Implemented `structure.xrd` as the second static physics adapter.
- The adapter uses existing `pymatgen.analysis.diffraction.xrd.XRDCalculator` with a deterministic CuKa-only policy.
- Generated deterministic artifacts: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json`.
- Registered the tool through Tool Registry and added strict params validation for radiation, two-theta range, intensity threshold, peak tolerance metadata, peak limit, HKL inclusion, and stem plot output.
- Added Mock Planner routing for XRD / powder diffraction / diffraction peak prompts.
- Added negative routing coverage so RDF, coordination histogram, full 3D viewer, WebGL, Brillouin-zone, phonon, Rietveld, fitting, and broadening prompts do not route to `structure.xrd`.
- Added adapter, fixture, registry, planner routing, artifact contract, security, and persisted execution tests.
- Browser/API evidence remains deferred to Phase 10E-5.
- No RDF, full interactive 3D viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, notebook/script extraction, external API workflow, experimental XRD fitting, Rietveld refinement, or advanced local environment classification was implemented.

## 2026-07-08 Phase 10E-5 XRD Browser/API Evidence

- Added API/artifact/security/negative-routing evidence for `structure.xrd` under `docs/phase10e/browser_api_evidence/phase10e5_xrd/`.
- Covered three bounded crystalline inputs: small CIF, small POSCAR, and generated pymatgen Structure JSON.
- Evidence generated: 40 redacted API captures, 12 artifact capture files, 6 local static preview pages, and an evidence manifest.
- Verified API/job flow through Mock Planner, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, adapter execution, artifact generation, result readback, and copied artifact audit.
- Verified artifacts: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json`.
- Security scan result: `NO_SECRET_PATTERN_HITS`; generated artifacts and preview pages contain no artifact JavaScript, active script tags, external URLs, WebGL renderer, Three.js renderer, or renderer bundle.
- Negative routing evidence confirms RDF, coordination histogram, full 3D viewer, WebGL, Brillouin-zone, phonon, experimental fitting, Rietveld, Voronoi, and CrystalNN prompts do not route to `structure.xrd`.
- Browser screenshot capture is blocked in this local environment because no in-app browser Node REPL tool is exposed and no Chrome/Edge/Firefox/Playwright/Puppeteer runtime is installed. No screenshot was fabricated.
- No new adapter was implemented, and no runtime main semantics or Phase 10E-4 XRD calculation policy were changed.

## 2026-07-08 Phase 10E-5R2 XRD Browser Screenshot Repair

- Repaired the Phase 10E-5 screenshot gap and upgraded Phase 10E-5 from `PARTIAL_PASS` to `PASS`.
- Detected system Chrome at `C:/Program Files (x86)/Google/Chrome/Application/chrome.exe` and launched it through Playwright `executablePath`.
- Captured six real browser-rendered frontend screenshots under `docs/phase10e/browser_api_evidence/phase10e5_xrd/screenshots/`.
- Browser audit confirms completed job display, artifact list, `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, and `recipe.json` previews.
- `xrd_plot.json` remains a static JSON / static chart metadata preview; rendered stem chart UI is deferred.
- No RDF, full viewer, WebGL renderer, Three.js, phonon, experimental fitting, or Rietveld refinement was implemented.
- No `structure.xrd` core semantics, schema version, runtime authority, Tool Registry semantics, QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, or PlanValidator boundary was changed.

## 2026-07-09 Phase 10E-6 RDF Policy Hardening

- Added Phase 10E-6 RDF policy hardening docs under `docs/phase10e/`.
- Retained Phase 10E-5 final status as `PASS` after Phase 10E-5R2 screenshot repair at commit `4c7e392`.
- Fixed the first RDF implementation policy:
  - periodic structures only with `pbc == [true, true, true]`;
  - `r_max_angstrom = 8.0` default, bounded `0.5..30.0`;
  - `bin_width_angstrom = 0.1` default, bounded `0.01..1.0`;
  - `normalization = number_density`;
  - ordered center-element to neighbor-element partial RDF pairs;
  - site, bin, neighbor, and partial-pair caps;
  - deterministic sorting and 6-decimal rounding.
- Planned RDF artifacts: `rdf.json`, `rdf_plot.json`, `summary.md`, and `recipe.json`.
- RDF readiness decision: `READY` for a single-scope Phase 10E-7 implementation using existing pymatgen periodic neighbor APIs and small periodic fixtures.
- This phase did not implement `structure.rdf`, did not modify `structure.xrd` or `structure.coordination_hist`, and did not change runtime semantics.
- Full interactive 3D viewer, WebGL renderer, Three.js renderer, Brillouin-zone 3D, phonon, trajectory RDF, experimental fitting, notebook extraction, script execution, and external API workflows remain deferred.

## 2026-07-09 Phase 10F-5 Static Physics Fixture Pack Replay Verification

- Replayed the Phase 10F-4 static physics fixture pack through the platform planner/job/runtime path.
- Fixture-pack replay result: `PASS`.
- Replayed cases:
  - `coordination_hist_small_crystal` -> `structure.coordination_hist`
  - `xrd_small_crystal` -> `structure.xrd`
  - `rdf_small_crystal` -> `structure.rdf`
- Verified selected tool IDs, expected artifact filenames, artifact schemas, static chart artifacts, summaries, recipes, deterministic recipe metadata, and no-JS/no-external-URL security flags.
- Updated fixture pack expected contracts with Phase 10F-5 candidate replay numeric values while keeping `official_pass_claim` false.
- Official examples PASS claims remain none because all replayed cases use `internal_regression` provenance.
- No notebook, external script, benchmark extraction script, external API, real LLM, new adapter, full viewer, WebGL renderer, Three.js renderer, or phonon scope was introduced.
- Recommended next scope: Phase 10F-6 fixture-pack evidence closure.

## 2026-07-10 Phase 10F-11 Viewer Scene Real Browser Evidence Hardening

- Added real browser evidence for the existing `viewer_scene.v1` JSON-only preview surface.
- Added a Playwright/system Chrome evidence runner at `apps/web/test/viewer-scene-browser-evidence.mjs`.
- Captured five browser-rendered screenshots plus DOM and network audit artifacts under `docs/phase10f/evidence/phase10f11_viewer_scene_real_browser/`.
- Covered valid minimal, warning/caps, invalid external-resource placeholder, invalid executable placeholder, and invalid schema-version fixtures.
- Hardened the existing frontend JSON-only preview to show inert `viewer_scene` summary and validation details even when schema validation is expected to fail.
- No full `structure.viewer_3d`, WebGL renderer, Three.js integration, renderer bundle, new adapter, planner routing change, runtime route, notebook, external API, or artifact JavaScript was introduced.

## 2026-07-12 Phase 10F-16 Scientific Structure Inspection

- Added canonical InstancedMesh atom picking, bounded A/B/C/D highlights, site inspector, bounded-bond neighbor summary, distance/angle/signed-dihedral measurement, and local PNG/artifact downloads.
- Measurements use displayed canonical Cartesian positions; minimum-image periodic measurement remains deferred.
- Real Chromium, Firefox, and WebKit evidence uses formal `structure.viewer_3d` jobs and adapter-generated artifacts.
- Canonical schema, formal tool identity, planner/runtime authority, and Phase 10D legacy artifacts remain unchanged.
- npm audit remains seven documented findings with no newly introduced renderer-reachable issue.

## 2026-07-12 Phase 10F-17 Periodic Crystal Inspection

- Added stable canonical-site plus image-offset identity throughout instancing, picking, highlights, inspector, snapshots, and measurements.
- Added bounded exact minimum-image distance and anchored periodic angle/dihedral, independently cross-checked against pymatgen including triclinic input.
- Added renderer-local `1x1x1` through `3x3x3` supercells with 2048-site and 8192-bond derived caps.
- Canonical artifacts and backend runtime semantics remain unchanged; cross-boundary bonds remain a documented contract gap.

## 2026-07-12 Phase 10F-18 Canonical Periodic Bond Topology

- Added backward-compatible v2 scene evolution with explicit periodic bond endpoints, displacement, distance, source, and authority.
- Both canonical viewer adapters generate bounded deterministic pymatgen periodic topology, including orthogonal/triclinic and self-periodic edges.
- Renderer supercells now replicate complete cross-boundary edges; the inspector exposes periodic neighbor identity and highlight actions.
- v1 remains valid as legacy same-cell topology. Distance-cutoff graphs remain non-authoritative.

## 2026-07-12 Phase 10F-19 Periodic Scene Integration Hardening

- Added exact additive capability metadata to `viewer_scene.v2`; bond semantics remain unchanged and v1 remains untouched.
- Added `phase10f19.viewer_assets_manifest.v2` with accurate periodic topology and no-renderer/no-WebGL declarations.
- Unified JSON preview topology counts and endpoint identity with the adapter contract and inspector.
- No renderer, dependency, planner, PlanValidator, or QueueWorkerRuntime semantics changed.

## 2026-07-12 Phase 10F-20 Legacy Viewer Schema Compatibility

- Added executable scene and manifest compatibility matrices mirrored in the frontend.
- Phase 10D is deprecated read-only/JSON-only; canonical v1 remains supported same-cell; v2 is current.
- Mock Planner redirects historical viewer requests to current v2 producers while direct legacy replay remains available.
- Automatic migration is intentionally absent because missing periodic endpoint identity cannot be inferred.

## 2026-07-13 Phase 10F-21 Viewer Performance Hardening

- Added immutable interactive/degraded/refused renderer budgets and fixed resource proxies.
- Near-cap scenes retain all validated topology with DPR 1/no antialias; over-budget scenes stop before engine creation.
- Added explicit generation-token stale protection, context-loss retry, and auditable demand-based scheduling.
- Three-browser/mobile/periodic performance evidence passed without dependency or schema changes.

## 2026-07-13 Phase 10F-22 Viewer Accessibility and Mobile Hardening

- Added a focusable viewer region with bounded keyboard rotate, pan, zoom, reset, and selection-clear actions.
- Added a synchronized semantic scene/topology summary, bounded polite announcements, and a capped semantic neighbor table.
- Removed the mobile scroll trap with `touch-action: pan-y`, established 44px mobile targets, and added reduced-motion/forced-colors policies.
- Chromium, Firefox, and WebKit evidence covers keyboard camera changes, 200% zoom, mobile orientation, one-canvas lifecycle, and zero external requests.

## 2026-07-13 Phase 10F-23 Advanced Picking and Measurement

- Added shared-LineSegments bond raycasting with stable canonical bond identity and fixed selected-bond overlay.
- Added ordered bounded endpoint selection, undo, keyboard atom/bond selection, and exact periodic identity announcements.
- Added deterministic inert `phase10f23.viewer_measurement.v1` local JSON download without scene/topology mutation.
- Chromium, Firefox, WebKit, and mobile evidence covers atom/bond picking, distance/angle/dihedral, cross-boundary endpoints, lifecycle, and network isolation.

## 2026-07-13 Phase 10F-26 Scientific Export and Reporting Foundation

- Added strict bounded PNG/JSON/Markdown export requests and responsive controls.
- Added light, dark, transparent, and high-DPI current-view capture with full renderer restoration.
- Added inert view-state JSON, scientific Markdown, and ordered SHA-256 manifest.
- Added stale cancellation, one-export concurrency, Blob URL cleanup, and safe error codes.
- Chromium, Firefox, WebKit, and mobile evidence observed zero external requests.
- PDF and full report layout remain deferred pending dedicated contract and dependency review.

## 2026-07-13 Phase 10F-27 Formal structure.viewer_3d Product Registration

- Moved the unique `structure.viewer_3d` registry entry to the platform-owned manifest without changing its adapter or runtime semantics.
- Froze the strict product input/output and capability contract around canonical inert scene v2 artifacts.
- Added live planner/job/artifact, three-browser/mobile, accessibility, lifecycle, performance, network, and security evidence.
- Explicit scene JSON remains `structure.viewer_scene`; advanced trajectory, phonon, Brillouin, volumetric, editing, and authoritative chemistry remain unsupported.

## 2026-07-13 Phase 10 Closure Regression Pack

- Added bounded backend, frontend, and real three-browser product composition entries.
- Closed six representative adapter paths through registry, planner, PlanValidator, runtime, artifact persistence/retrieval, and validators.
- Added current/legacy, determinism, fallback, lifecycle, capability-truth, network, and secret evidence.
- Integrated exact closure gates into existing unit, frontend, and PostgreSQL/Redis/MinIO CI jobs without new dependencies.

## 2026-07-14 Phase 10H-1 Phonon Bands

- Implemented the unique planner-visible `phonon.band` adapter for validated canonical JSON and bounded static phonopy band.yaml.
- Added deterministic canonical band/summary/manifest, parse report, Plotly, table, and recipe artifacts through QueueWorkerRuntime.
- Added canonical-only lazy local Plotly preview with branch/segment preservation, negative values, refusal budgets, table/JSON fallback, and cleanup.
- Chromium, Firefox, WebKit, mobile, API, determinism, network, and security evidence passed without new dependencies.
- DOS, combined view, eigenvectors, animation, and phonon calculation remain deferred.

## 2026-07-14 Phase 10H-2 Phonon DOS

- Implemented the unique planner-visible `phonon.dos` adapter for canonical DOS and bounded phonopy total/projected text wrappers.
- Added exact THz/density-Jacobian conversion, explicit total-mode/unit-area normalization, negative-region preservation, and atom/species projection identity.
- Added DOS-specific summary/manifest extensions, report, plot, table, recipe, runtime persistence, and validated local Plotly preview.
- Chromium, Firefox, WebKit, mobile, accessibility, API, determinism, network, and security evidence passed without new dependencies.
- Combined band+DOS, pymatgen serialized input, directional projections, eigenvectors, animation, and calculation remain deferred.

## 2026-07-17 Phase 10J Volumetric Data Contract

- Added five strict inert contracts for grid, payload, field, dataset, and manifest.
- Fixed real-space row-vector affine math, endpoint-excluded periodic grids, `ijkc` component-fastest storage, and structure/lattice binding.
- Added little-endian float32/float64 inline, raw, deterministic gzip, and bounded whole-i-slab chunk payloads with layered SHA-256 identities.
- Added explicit quantity/unit, normalization/integral, collinear/non-collinear spin, complex scalar, potential gauge, statistics, caps, and typed validation.
- Added deterministic fixtures, independent standard-library references, binary payloads, replay hashes, and decompression/security evidence.
- No parser, adapter, tool, planner route, runtime execution, renderer, isosurface, external resource, or dependency was added.

## Phase 10J-1 - Volumetric Parser / Adapter

- Added bounded streaming VASP CHGCAR/CHG/LOCPOT/ELFCAR/PARCHG and single-scalar Gaussian CUBE parsing into the existing Phase 10J contracts.
- Added `VolumetricData`, formal `structure.volumetric_data`, strict params, planner routing, PlanValidator/runtime execution, deterministic binary artifacts, and JSON-only metadata preview.
- Verified canonical order, units, spin channels, affine grids, hashes, a 128-cubed bounded run, typed cap rejection, network isolation, and no artifact execution.
- Renderer, slice, isosurface, multi-orbital CUBE, and production-scale inputs above the parser cap remain deferred.

## 2026-07-20 Phase 10J-2 Isosurface Renderer

- Implementation commit `f6edcac347f2f7fffdbda47b1f72ad493c8edae8` passed local frontend `241` tests, backend `713 passed, 24 skipped`, typecheck/build, real Chromium/Firefox/WebKit WebGL2 and mobile evidence; current-head CI run `29744316126` passed unit, frontend/typecheck/build, PostgreSQL/Redis/MinIO service-backed integration, and no-skipped gates.
- Completion record `c7669619b1444076bc47e8f084ddc2d5df5ce783` passed current-head CI run `29745406355`; the result was verified and the completed Phase 10J-2 queue block is archived.

- Added strict frontend validation and bounded job-scoped raw/gzip/chunked payload retrieval with SHA-256 revalidation.
- Added application-owned Worker extraction using deterministic marching tetrahedra, periodic logical halo, affine/triclinic coordinates, gradient normals, welding, and mesh caps.
- Added lazy application-owned Three.js rendering, structure/cell overlay, layers, picking, clipping, projection, camera controls, PNG, fallbacks, and full disposal.
- Real Phase 10J-1 CHGCAR artifacts rendered in Chromium, Firefox, WebKit, and mobile with zero external requests.
- Slice, direct volume rendering, vector/complex derivation, and scientific field analysis remain deferred.

## 2026-07-20 Phase 10J-3 Charge / Spin Density Product

- Added source-native electron density and explicit signed charge-density product semantics over `structure.volumetric_data`.
- Added allowlisted collinear `spin_up`/`spin_down` fields with fixed formula IDs, source provenance, exact relationships, and full-cell integrals.
- Added product UI with total/spin-difference/up/down modes, paired signed isosurfaces, symmetric threshold lock, warnings, and mobile-safe layout.
- Closed real QueueWorkerRuntime-to-adapter artifacts, Chromium/Firefox/WebKit/mobile browser evidence, performance, accessibility, network, and secret-scan markers.
- Bader, atomic partitioning, non-collinear vector product, potential, slices, and direct volume remain deferred.

## 2026-07-22 Phase 10J-4 Electrostatic Potential Product

- Preserved real LOCPOT as source-defined `local_potential` in electronvolt; no electrostatic-component, vacuum, Fermi, or work-function inference.
- Added strict frontend potential reference/statistics mapping, source-native/cell-average-zero/selected-point-zero gauges, source-contour-preserving layer identity, trilinear point sampling, gauge-invariant point differences, and three Worker-reduced raw lattice-axis profiles with linked 3D planes.
- Reused the Phase 10J-2 Worker/Three.js renderer and captured Chromium/Firefox/WebKit/mobile runtime, profile, performance, accessibility, network, and security evidence.
- Vacuum/work-function/Fermi alignment, cross-calculation alignment, macroscopic averaging, arbitrary slice/path, and direct volume remain deferred.
- Local closure after the final runner hardening passed 258 frontend tests and `722 passed, 24 skipped, 62 warnings` backend tests, typecheck, production build, the historical volumetric/charge-spin/Phase 10 browser pack, and the Phase 10J-4 Chromium/Firefox/WebKit/mobile evidence. The live evidence records one WebGL2 canvas per browser, zero console/page errors, zero external requests, source-contour preservation, three profiles, point difference, PNG signature, and the bounded `128^3` float64 near-cap test. Docker-backed service integration remains a current-HEAD CI gate; the configured npm audit endpoint remains unavailable.
