# OPEN_QUESTIONS

## 2026-07-06 Phase 10B Second Batch pymatviz Adapter Planning

- **Closed for planning: second-batch direction.** Phase 10B recommends composition visualization as the next implementation area rather than jumping directly to structure viewer, XRD/RDF, phonon, or Brillouin zone work.
- **Closed for planning: Phase 10B-1 recommended scope.** The next implementation prompt is scoped to `composition.ptable_heatmap`, `composition.elements_hist`, `composition.chem_sys_treemap`, `composition.chem_sys_sunburst`, and `composition.formula_statistics`.
- **Still open: evidence-grade composition adapters.** Existing registry entries for some composition tools need Phase 10B-1 hardening and Phase 10B-2 browser/API/artifact evidence before they can be treated as official direct-case evidence.
- **Still open: structure/physics adapters.** `structure.viewer_3d`, XRD, RDF, phonon, Brillouin zone, and related physics workflows need a separate Phase 10C+ planning/evidence strategy.
- **Still open: notebook/script extraction.** Extraction-required official examples remain outside the current direct benchmark scope.

## 2026-07-06 Phase 10A-2 Browser/API Evidence for First Batch Adapters

- **Closed: browser/API/artifact evidence for first-batch tools.** MatPES scatter, MatPES histogram, Ward distribution summary, Ward histogram, Ward correlation, and Ward composition summary now have project-local redacted API captures, artifacts, screenshots, summaries, and manifests.
- **Closed: first-batch Plotly JSON evidence contract.** `viz.scatter` and `viz.histogram` now write top-level chart metadata required by the benchmark evidence while keeping the nested Plotly figure for rendering.
- **Closed: composition prompt routing ambiguity.** Composition distribution prompts now route to `composition.summary` before generic histogram/distribution routing.
- **Still open: remaining official examples.** The other 59 official examples remain outside this browser/API evidence phase and keep their benchmark statuses from Phase 10A-0.
- **Still open: multi-step DAG/data-dependency execution.** The evidence verifies single-step adapter execution; combined workflows remain future work.
- **Still open: CI/browser evidence policy.** Browser/API evidence is committed as documentation evidence but is not a default CI gate.
- **Still open: broader adapter coverage.** Phonon, Brillouin zone, advanced widgets, XRD/RDF, classification curves, and richer report/export workflows remain future phases.

## 2026-07-06 Phase 10A-1 First Batch Adapter Implementation

- **Closed: MatPES richer first-batch plot/table tools.** The platform now has registry-gated `viz.scatter`, `viz.histogram`, and `table.distribution_summary` tools that can serve MatPES scatter/distribution/table-summary prompts within the current single-step execution model.
- **Closed: Ward first-batch distribution/correlation tools.** The platform now has registry-gated `table.distribution_summary`, `viz.histogram`, and `viz.correlation` tools for Ward-style tabular distribution and numeric correlation prompts.
- **Closed at adapter level: safe composition summary.** `composition.summary` can summarize a stable formula/composition field when present, including Ward's `composition` column; it must not infer or fabricate composition results when no formula-like field exists.
- **Still open: browser evidence for new tools.** This phase adds adapters and tests; full browser-click evidence for scatter/histogram/correlation/distribution-summary outputs should be captured before freezing a demo evidence baseline for these new outputs.
- **Still open: multi-step DAG/data-dependency execution.** The new tools are single-step executable plans. Combined workflows such as metrics plus scatter plus report still require DAG/data-dependency scheduling or explicit multi-step support.
- **Still open: remaining official examples.** The 27 extraction-required, 20 mapping-only, and 12 future-scope official examples remain outside this phase.
- **Still open: broader visualization adapters.** Phonon, Brillouin zone, advanced widgets, XRD/RDF, classification curves, and richer report/table/export workflows remain future adapter phases.

## 2026-07-05 Phase 9D True LLM Live Verification

- **Closed: true live LLM full-chain evidence captured.** The Gemini OpenAI-compatible path produced redacted evidence from live provider output through PlanValidator, persisted AnalysisPlan, `jobs.plan_id`, QueueWorkerRuntime, Tool Registry + Adapter, Artifact/Result generation, and Phase 9C UI display.
- **Closed: final gated live rerun passed.** `python -m pytest -q -m llm_integration` passed with Gemini 3 Flash Preview, proving the current OpenAI-compatible Gemini path can run the full persisted planner job chain.
- **Open: Antigravity model requires a different provider contract.** Gemini reports `antigravity-preview-05-2026` only supports Interactions API, not OpenAI-compatible chat/completions. Supporting it would be a future provider path, not Phase 9D OpenAI-compatible verification.
- **Closed: live LLM parameter aliases could pass persistence and fail only at adapter runtime.** PlanValidator now validates each step's params against the registered tool `paramsSchema` before persistence.
- **Closed: Phase 9D evidence redaction.** The local evidence pack under `docs/llm-live-verification/phase9d/` was scanned for key/token strings and did not contain the API key or auth token header.
- **Still open: production secret encryption/KMS.** Phase 9D used env/SecretStore safely but does not implement production envelope encryption.
- **Still open: multi-step DAG/data-dependency execution.** Live verification covered a simple executable plan path, not DAG scheduling.
- **Still open: worker process supervision/dead-letter policy.** Queue semantics remain the existing Phase 8B/9C path.
- **Still open: broader pymatviz adapter coverage.** The live run verified metrics/report artifacts, not the full official visualization inventory.

## 2026-07-05 Phase 9D LLM Configuration Path Repair

- **Closed: UI provider config looked disconnected from planner jobs.** The UI already passed provider config into `/planner/jobs`; this repair adds an explicit no-network resolve API so the UI can show the current task provider status without relying on env-default status.
- **Closed: env settings could override explicit UI model/timeout settings.** Explicit `PlannerUserConfig` now wins when supplied; env remains the source for env-only live tests.
- **Still open: true live LLM verification.** The gated full-chain test exists but was not run because live LLM env is not configured in the current shell.
- **Still open: UI SecretStore and CLI env are separate paths.** This is acceptable for Phase 9D, but a later production config flow may unify operator-managed provider config and user BYOK secrets.
- **Still open: production secret encryption/KMS.** Secret UX remains dev/test in-memory and redacted, not production envelope encryption.

## 2026-07-05 Phase 9C UI/UX Redesign Docs Baseline

- **Closed: independent right-side Result Inspector.** The Phase 9C design explicitly does not use a persistent right result panel. Results belong to the main `结果与导出` tab.
- **Closed: old three-column frontend baseline as recommended direction.** The old right Agent panel and bottom result tabs are legacy context. The recommended direction is top global context bar, left data-context viewer, and main three-tab workspace.
- **Closed: where Agent process vs conversation vs results live.** All three live inside the main workspace as mutually exclusive tabs: `Agent 过程`, `对话与 Plan`, `结果与导出`.
- **Closed at baseline level: resize/collapse and main-tab implementation.** `PlannerWorkbench` now includes a collapsible/resizable left data-context viewer and mutually exclusive main tabs with tests.
- **Still open: responsive drawer polish.** The baseline is responsive, but a dedicated mobile drawer interaction can be refined later.
- **Still open: exact visual styling.** This docs baseline fixes information architecture, not final colors, typography, spacing, or component library details.

## 2026-07-05 Phase 9B Official Direct Examples Semantic Refinement

- **Closed: Ward direct-uploadable semantic blocker.** Ward metallic glass evidence no longer treats `D_max` and `dTx` as target/prediction regression columns. It now uses `table.numeric_summary` for independent numeric and categorical summaries.
- **Closed: MatPES stale prompt evidence.** Fresh MatPES browser evidence now uses the PBE vs r2SCAN prompt and no longer contains the stale `y_true` / `y_pred` request in the captured browser text.
- **Still open: richer official visualization coverage.** Ward composition/element distributions, periodic-table heatmaps, histograms/scatter plots, and richer reports remain future adapter/report work. MatPES histogram/table/report outputs also remain future work.
- **Still open: full official examples suite.** This pass only regenerated the two direct-uploadable cases requested by the user.

## 2026-07-04 Phase 9B Official MatPES Example Blocker Repair

- **Closed: MatPES official CSV metrics blocker.** The evidence-pack failure for `matpes_atomic_energies_csv` is fixed. Mock Planner now uses DataProfile columns and selected `PBE` / `r2SCAN` for `ml.basic_metrics`; the browser rerun completed with one ToolCall and one artifact.
- **Still open: complete official examples suite execution.** Only the previously failed MatPES direct-uploadable case was rerun in this repair pass. The remaining official examples, including `ward_metallic_glasses_csv_xz`, script/notebook cases, MVP/V1 mapped README demos, and future-scope cases still require separate evidence-pack execution.
- **Still open: richer non-ML prompt/tool routing.** The current fix handles metric plans for role-less numeric tables. Composition/structure datasets should later steer to composition or structure tools when the profile and user intent indicate those domains.

## 2026-07-04 Phase 9B Browser + Durable Worker Resolver Closure

- **Closed: browser verification after API/Web restart.** The in-app browser loaded the local workspace, ran the demo workflow with Mock Planner, showed completed status, plan provenance, timeline events, artifact gallery, report/recipe summary, and ToolCall details. No real API key was entered.
- **Closed: worker-side durable object-store resolver.** `run_queued_job(job_id)` now builds a settings-driven SQLAlchemy repository factory, configured ArtifactStorage, and `DurableObjectStoreResolver`, so an out-of-process worker can rebuild `ml_table`/`structures`/`formulas` from persisted normalized exports.
- **Closed: PostgreSQL planner runtime missing durable object resolver.** The PostgreSQL planner runtime construction path now installs the same artifact storage and resolver.
- **Still open: true LLM live verification.** The gated provider path remains implemented, but no live provider run was executed in this closure.
- **Still open: production upload service hardening.** The worker can now read persisted normalized exports, but the current demo upload path still goes through the Phase2 local runtime. A production upload path should persist dataset/profile/normalized exports directly through SQL and MinIO/S3.
- **Still open: production secret encryption/KMS, multi-step DAG/data-dependency execution, worker supervision/dead-letter, and advanced material viewer polish.**

## 2026-07-04 Phase 9B Runtime Data Binding Follow-up

- **Closed: local demo planner jobs staying queued without a worker process.** In the default in-memory development path, `/planner/jobs` now enqueues and auto-drains the job through `QueueWorkerRuntime.handle_job(job_id)` only when no Redis queue is configured and no custom repos/runtime are injected.
- **Closed: uploaded dataset objects not reaching the local queue worker.** `QueueWorkerRuntime` now supports an object-store resolver, and the default planner runtime resolves Phase2 uploaded/demo dataset objects by `dataset_id` before executing the persisted plan.
- **Closed: planner prompt/profile context did not expose real uploaded columns.** Planner preview/jobs now use the real Phase2 `DataProfile` when available, and the prompt describes normalized inputRef conventions.
- **Closed: executable plans could omit dataset inputRefs for uploaded data.** Uploaded dataset plans now fail before persistence/job/enqueue when their steps require an available normalized object but omit or misname the required inputRef.
- **Remaining: durable normalized-object loading for out-of-process Redis workers.** The current follow-up closes the local in-memory demo path and adds a resolver seam. Production Redis workers that run in a separate process still need durable normalized object storage/loading for uploaded datasets instead of relying on process-local Phase2 memory.
- **Remaining: browser automation after restart.** API E2E and frontend tests passed, but final browser click-through after restart could not be automated because the browser plugin native bridge was unavailable in this environment.

## 2026-07-04 Phase 9B Frontend/API Follow-up

- **Closed: browser preflight 405 for Phase 9B workspace APIs.** The affected routes were implemented, but the FastAPI app lacked CORS middleware. Local/demo origins are now configured by default and overrideable through `MDI_CORS_ORIGINS` / `CORS_ORIGINS`.
- **Closed: invalid plan response echo for `/planner/jobs`.** Validation failure now returns no raw rejected plan, so credential-like params rejected by PlanValidator are not echoed to the frontend/API caller.
- **Closed: runtime health config-only reporting.** `/health/runtime` now runs safe light probes where a backend is configured and returns redacted `unknown` component status on probe failure.
- **Closed: full Planner workbench i18n string extraction for user-facing labels.** Remaining hard-coded Chinese labels in `PlannerWorkbench.tsx` were moved into the `zh-CN` / `en-US` message files, and English-mode regression assertions cover key labels.

## 2026-07-04 Phase 9B Follow-ups (Demo-ready AI Planner Workspace)

- **Phase 9B product workspace is implemented locally.** The Planner UI now has default Chinese i18n, provider settings, Secret UX, dataset/profile/demo workflow, region-specific empty states, error explanations, grouped artifacts, report/recipe summary, and user/developer mode layering.
- **Service-backed runtime verification for this commit is pending CI.** This local machine has no Docker CLI; PostgreSQL + Redis + MinIO integration must be confirmed by GitHub Actions for the Phase 9B commit. Local integration skips must not be treated as passed integration.
- **Live LLM verification is still not claimed.** Phase 9B did not run a live provider test. The Phase 9A gated path remains available only when explicit `MDI_RUN_LLM_INTEGRATION=1` and provider env are configured.
- **Production secret encryption/KMS remains deferred.** Phase 9B improves Secret UX and no-plaintext response shape, but does not implement production envelope encryption.
- **Multi-step DAG/data-dependency execution remains deferred.** The workbench previews steps and provenance but does not implement DAG scheduling, node editing, or data-dependency execution.
- **Worker process supervision and dead-letter policy remain deferred.** Phase 9B does not change queue worker core semantics.
- **Advanced material viewer polish remains deferred.** Artifact display is grouped and productized, but full material 3D viewer polish remains future work.

## 2026-07-03 Phase 9A Follow-ups (Gated True LLM Provider)

- **Gated OpenAI-compatible provider path is implemented locally.** The provider can be selected explicitly and configured by `MDI_LLM_*` environment variables while the default provider remains mock/deterministic-safe.
- **Live LLM verification is not claimed locally.** The gated `llm_integration` test exists, but local env does not include the required live provider settings, so `python -m pytest -q -m llm_integration` skips by design.
- **Default CI must remain real-LLM-free.** No default workflow should require `MDI_LLM_API_KEY` or call an external provider.
- **Service-backed runtime verification for this commit is pending CI.** This local machine has no Docker CLI; PostgreSQL + Redis + MinIO integration must be confirmed by GitHub Actions for the Phase 9A commit.
- **Prompt/completion debug logging remains deferred.** Raw prompts and completions are not persisted by default; any future debug path must be opt-in and redacted.
- **Production secret encryption/KMS remains deferred.** Phase 9A reads keys from env/config and preserves no-leak boundaries, but it does not implement production BYOK encryption.
- **Multi-step DAG/data-dependency execution remains deferred.** Phase 9A changes provider selection only; execution semantics remain Phase 8B persisted sequential plan execution.
- **Worker process supervision and dead-letter policy remain deferred.** Queue worker core behavior was not changed.
- **Advanced material viewer polish remains deferred.** No frontend visualization redesign was included.

## 2026-07-03 Phase 8C-P1 Follow-ups (UX Compliance Closure)

- **SSE/EventSource timeline P1 is locally closed.** The Planner workbench now opens an EventSource path for persisted JobEvents through `/planner/jobs/{job_id}/events/stream`, and polling remains only as fallback.
- **Report/Recipe Summary P1 is locally closed.** The UI now has a separate report/recipe summary area instead of relying on the artifact/result list alone.
- **Dataset/Profile selector P1 is locally closed.** The UI now offers API-backed dataset/profile selection using existing read endpoints and retains manual ID fallback when discovery/profile reads are unavailable.
- **Phase 8C-P1 CI gate is closed for the implementation commit.** GitHub Actions run `28664159687` on commit `4d0c241` succeeded, including service-backed PostgreSQL + Redis + MinIO integration with 19 passed, 0 skipped, 0 failed.
- **True LLM integration remains deferred.** No production LLM provider enablement or live LLM test gate was added.
- **Advanced multi-step DAG/data-dependency execution remains deferred.** No scheduler or DAG editor semantics were added.
- **Production secret encryption remains deferred.** No KMS/envelope encryption work was done.
- **Worker process supervision and dead-letter policy remain deferred.** Worker runtime semantics were not changed.

## 2026-07-03 Phase 8C Follow-ups (Frontend Planner UX)

- **Frontend Planner UX baseline is closed/frozen.** The frontend can create Planner Jobs through `/planner/jobs`, display the validated persisted plan, show `planId`/`planHash`, display `job.plan_id -> analysis_plans.id`, surface `plan.loaded`, and show ToolCall/Artifact/Result plan provenance. Implementation commit `9967c5b` passed GitHub Actions run `28646226271`.
- **Validation-failure UX is closed at the baseline level.** The frontend now clearly states that no AnalysisPlan was saved, no Job was created, and nothing was enqueued; it does not poll job status or show fake IDs after validation failure.
- **Phase 8C CI gate is closed for the implementation commit.** GitHub Actions run `28646226271` succeeded, including service-backed PostgreSQL + Redis + MinIO integration with 19 passed, 0 skipped, 0 failed.
- **True LLM integration remains deferred.** The frontend uses the existing backend planner provider path; production real-provider enablement and live LLM tests remain future work.
- **Advanced multi-step DAG/data-dependency execution remains deferred.** The UI previews steps and provenance, but it is not a drag/drop DAG editor and does not add scheduler semantics.
- **Production secret encryption remains deferred.** Phase 8C displays provenance and validation errors; it does not implement KMS/envelope encryption.
- **Worker process supervision and dead-letter policy remain deferred.** Phase 8C did not alter worker operations.
- **Advanced material viewer polish remains deferred.** Artifact display is provenance-oriented and does not yet implement a full material 3D viewer workflow.

## 2026-07-03 Phase 8B Follow-ups (Persisted Plans + Queue Runtime)

- **Closed/frozen: QueueWorkerRuntime + persisted AnalysisPlan execution.** The main worker path now loads `job.plan_id`, fetches the persisted `AnalysisPlan`, reconstructs it, and executes exact `steps`; tests prove a persisted 1-step plan creates exactly 1 ToolCall, not the deterministic 5-tool fallback.
- **Closed/frozen: PostgreSQL persisted plan schema.** Alembic revision `0002_phase8b_plans` adds `analysis_plans`, `jobs.plan_id`, and required indexes. CI verifies these through Alembic upgrade head against PostgreSQL.
- **Closed/frozen: service-backed Phase 8B gate.** This local machine has no Docker CLI, so the PostgreSQL + Redis + MinIO Phase 8B integration test could not be run locally. GitHub Actions run `28631817086` on Phase 8B code acceptance commit `962c429` ran Phase 6 + Phase 8B integration with 19 passed, 0 skipped, 0 failed.
- **Frontend Planner UX remains deferred to Phase 8C.** Do not start Phase 8C until Phase 8B is frozen by CI-backed service integration.
- **Multi-step dependency graph remains deferred.** Phase 8B executes persisted steps in order and preserves the existing `inputRefs`/`object_store` mechanism; it does not add DAG scheduling or inter-step artifact binding.
- **True LLM integration remains deferred.** Default tests continue to use MockLLMProvider/fake transport; real OpenAI/DeepSeek service tests need a separate opt-in gate and redaction policy.
- **Production secret encryption remains deferred.** Plan persistence rejects credential-like params, but the production `EncryptedSecretStore`/KMS path is still not implemented.

## 2026-06-27 Phase 8A Follow-ups (Plan Execution Bridge)

- **LLM→execution closed loop is now CLOSED at the local-runtime level.** `/planner/jobs` (execute=True) runs the EXACT validated LLM plan through `Phase2ProductRuntime` → Tool Registry → Adapter, proven by `test_runtime_executes_exact_provided_plan_one_tool_call` (1 step → 1 ToolCall, not deterministic 5).
- **Remaining: QueueWorkerRuntime + PostgreSQL plan persistence.** Execution currently uses the in-memory synchronous `Phase2ProductRuntime`. The validated plan is NOT yet persisted to PostgreSQL nor enqueued onto the Redis `QueueWorkerRuntime`. Wiring `analysis_plan` into the queue worker + a `persisted_plans` table (Alembic migration) is the next integration step.
- **Multi-step dependency graph deferred.** The bridge executes steps in plan order; there is no inter-step data-dependency resolution beyond the existing inputRefs/object_store mechanism. A real DAG executor is future work.
- **Plan input binding is still conventional.** The LLM plan must reference the conventional `ml_table` (or `formulas`/`structures`) normalized object refs. A general field-mapping/resolution layer between LLM logical refs and dataset objects is future work.
- Real LLM integration, production envelope encryption, frontend Planner UX, and plan auto-repair remain deferred (unchanged from Phase 7 records).

## 2026-06-27 Phase 7 Follow-ups (LLM Planner + BYOK)

- **Production envelope encryption is NOT implemented.** `EncryptedSecretStore` is a placeholder that raises `NotImplementedError`. Only `InMemorySecretStore` works, and it is for dev/test ONLY — it holds plaintext values in memory and must never be used in production. A real backend (KMS, Fernet, or HashiCorp Vault) is required before any production BYOK use.
- **LLM → execution closed loop is NOT complete.** `POST /planner/jobs` generates an LLM plan, validates it, and then creates a job via `Phase2ProductRuntime.create_job()`. However, that runtime internally regenerates its own **deterministic** plan (`build_phase2_plan`) — the validated LLM plan is currently NOT the plan that executes. The job status returned is "created" (in-memory Phase 2 path), not a real enqueue onto Redis/PostgreSQL. Wiring the validated LLM plan into the real QueueWorkerRuntime + Tool Registry + Adapter execution path is deferred to a later phase.
- **Real OpenAI/DeepSeek integration tests are optional and not in the default suite.** All Phase 7 tests use `MockLLMProvider` or a fake transport. A real LLM integration test (gated behind an env var like `MDI_RUN_LLM_INTEGRATION=1` + `OPENAI_API_KEY`) is future work; it must never run in the default `pytest -q`.
- **Prompt / completion logging policy is undecided.** Currently no prompt or completion is logged. If debug logging is added later, it MUST pass through `redact_credential_values()` and default to off. A formal policy (what to log, retention, redaction guarantees) is open.
- **Runtime full-chain secret-leak audit is not yet done.** Phase 7 has unit-level redaction tests and a secret-list-no-plaintext test, but no end-to-end audit proving secrets never reach JobEvent / Artifact metadata / Recipe / Report in the live runtime. The current code has no path that writes secrets to those sinks, but an explicit audit test is future work.
- **Plan auto-repair is intentionally not implemented.** PlanValidator is strict — invalid plans are rejected, not repaired. Auto-repair (ask the LLM to fix its own invalid plan) is deferred to avoid silently executing mutated plans.

## 2026-06-26 Phase 6 Follow-ups

- **Acceptance: CONDITIONAL PASS.** No P0 blocker in the code or test design. All 18 integration tests skip cleanly because Docker is not available on this machine. Git is clean at commit `e3c7a73`.
- P0-2 (integration tests all skipped) is unresolved at the infrastructure level: Docker must be installed and services started before live tests can run. This is by design — tests skip rather than fail on missing infrastructure.
- P0-3 (Alembic test) is resolved: the committed test calls real `alembic.command.upgrade(alembic_cfg, "head")` with downgrade+reupgrade cycle and index existence verification.
- P0-4 (service-backed loop) is resolved: the committed test uses real Tool Registry + BasicMetricsAdapter through `execute_tool_request()`, not a fake executor.
- **Cannot enter Phase 7** until: (1) Docker is installed, (2) `docker compose up -d postgres redis minio` succeeds with all services healthy, (3) `MDI_RUN_INTEGRATION=1 python -m pytest -q -m integration` passes with zero skipped tests.
- Concurrent JobEvent seq test uses `ThreadPoolExecutor(max_workers=6)` with 30 concurrent appends — unit-level concurrency smoke; true multi-process/container stress testing remains a production-readiness task.
- Queue integration tests use synchronous `handle_job()` after enqueue (simulating worker process fetch). Real RQ multi-worker deployment remains later work.
- MinIO presigned URL HTTP GET verification requires the caller on the Docker network or localhost. The API-level test (URL contains bucket/key, expires, content_type) is in place.
- CI pipeline needs a service-backed job: `docker compose up -d postgres redis minio` → wait healthy → `MDI_RUN_INTEGRATION=1 python -m pytest -q -m integration`.

## 2026-06-26 Phase 5 Follow-ups

- No P0 blocker is open after the Phase 5 PostgreSQL runtime, queue worker, and MinIO integration pass.
- PostgreSQL runtime configuration, Alembic env override, Docker Compose infrastructure, and runbook now exist. A later deployment pass still needs pool sizing, migration rollback policy, backup/restore policy, and production secret injection.
- QueueWorkerRuntime now supports repository-backed job handling, duplicate enqueue stability, and retry idempotency tests. Later work still needs worker process supervision, dead-letter queues, exponential backoff policy, visibility timeout policy, and operational metrics.
- PostgreSQL JobEvent seq allocation now uses a transaction-scoped advisory lock keyed by `job_id`. Multi-process/container stress testing remains a production-readiness task beyond the default unit suite.
- S3/MinIO storage now supports live put/get/exists/presigned-url behavior when a boto3-compatible client or credentials are configured. Bucket creation policy, bucket lifecycle rules, object retention, access-control checks, and preview object policy remain open.
- Integration tests are intentionally opt-in with `MDI_RUN_INTEGRATION=1`; CI still needs a service-backed job that starts PostgreSQL, Redis, and MinIO and runs the integration marker.

## 2026-06-26 Phase 4 Follow-ups

- No P0 blocker is open after the Phase 4 production persistence hardening pass.
- Alembic baseline files and SQLAlchemy metadata now exist, but the runtime still needs a real PostgreSQL database URL, migration execution policy, pool sizing, and deployment runbook.
- Repository transaction boundaries are available through `RepositorySession` / `UnitOfWork`; application services still need to adopt them when the local Phase 2 runtime is replaced by durable workers.
- JobEvent seq allocation is concurrency-tested with repository-level in-process locking. Before multi-process workers, PostgreSQL should use row locking, advisory locking, or a per-job sequence allocation strategy.
- ToolCall and Artifact writes have idempotent repository behavior. A later queue phase still needs explicit worker attempt records, retry policy, crash recovery policy, and dead-letter handling.
- S3/MinIO metadata mapping remains clear, but live presigned URL generation, bucket policy, retention/lifecycle rules, and access-control checks remain future work.

## 2026-06-26 Phase 3 Follow-ups

- No new P0 blocker is open after the Phase 3 persistence foundation pass.
- Repository interfaces and SQLite-testable SQLAlchemy implementations now cover Project, Dataset, DataProfile, Job, JobEvent, ToolCall, Artifact, Recipe, and Report. A later phase still needs production transaction boundaries, Alembic adoption, PostgreSQL connection/session lifecycle, and idempotent worker writes.
- JobEvent seq cursor semantics are implemented for the local runtime and repository layer, including in-process duplicate-seq protection. A later phase still needs database-level multi-process locking strategy, production SSE backpressure, heartbeat, auth checks, and reconnect/load behavior under concurrent workers.
- Artifact storage mapping now covers local files and S3/MinIO-compatible metadata. A later phase still needs a live object-storage client, presigned URL policy, access-control checks, retention/lifecycle policy, and preview generation strategy.
- `reports` now has repository coverage and migration metadata. Report-specific API list/detail routes beyond artifact/report downloads remain future work.
- `S3CompatibleArtifactStorage.signed_url()` intentionally returns a `not_implemented` placeholder until live credentials, bucket policy, and signed URL expiry rules are decided.

## 2026-06-25 Phase 2 Acceptance Audit Follow-ups

- No new P0 blocker is open after the Phase 2 acceptance hardening pass.
- Phase 2 Recipe and AnalysisPlan schema shape is now aligned with the shared schema. Future schema changes should update `docs/13_SHARED_SCHEMA_SPEC.md`, Python schemas, TypeScript schemas, runtime emitters, and tests together.
- Ignored verification outputs (`node_modules`, `.next`, pytest cache/temp directories, Python bytecode, and TypeScript build info) are intentionally not part of Git or archive handoffs and should be cleaned before packaging.

## 2026-06-25 Phase 2 Follow-ups

- Phase 2 now proves the repository/API shape with in-memory state. A later phase still needs to decide the exact PostgreSQL repository interfaces and migration path for projects, datasets, jobs, tool calls, events, artifacts, recipes, and reports.
- Phase 2 artifact lookup reads local files directly. A later phase still needs to map the same API contract to MinIO/S3 signed URLs and access-control checks.
- Phase 2 job creation drains the LocalWorkerRuntime immediately for deterministic acceptance. A later phase still needs durable queue semantics, retry/cancel behavior, and SSE cursor persistence.
- Phase 2 supports local file paths and inline small text uploads for acceptance. Production upload sessions, object-storage direct upload, and file security limits remain future work.

## 2026-06-25 Phase 1 Acceptance Follow-ups

- Phase 1 now accepts `preview_png` as a required artifact family, but the MVP implementation may use a minimal valid PNG fallback when Kaleido/Chromium is unavailable. V1 still needs a decision on whether render workers must install and manage Kaleido/Chromium for real chart snapshots.
- Phase 1 product-flow acceptance is currently proven by an in-memory deterministic runtime. Next phase must decide the exact repository/API shape for replacing demo project/dataset/job/artifact state.
- The `/jobs/{job_id}/events/stream` route now exposes an SSE-style boundary without `sse-starlette`. Next phase must decide whether to keep plain `StreamingResponse` or introduce a Starlette-compatible SSE dependency.
- Phase 1 engineering reproducibility is now fixed on `uv.lock` for Python and `apps/web/package-lock.json` for frontend npm installs. Future dependency changes should update those lockfiles in the same commit as dependency declarations.

## Product

- 产品正式名称优先采用 Material Insight Studio、MatViz Agent Platform，还是 LabPilot Materials Workspace？
- V1 是否支持公开分享、匿名报告链接和外部协作者查看？
- V1 是否支持 PDF 报告导出？
- Guided / Expert 模式的最小可用范围是什么？

## Architecture

- 何时从 FastAPI 模块化单体拆分为独立 Data / Agent / Visualization 服务？
- LabPilot 集成时采用 NestJS BFF、API Gateway 代理，还是 iframe / embedded workspace？

## Frontend

- V1 是否支持用户自定义 Dashboard 拖拽布局？
- V1 是否评估 native MatterViz React 集成，替代部分 iframe artifact？
- 3D Viewer 的全屏、截图和结构选择器交互细节如何设计？

## Backend

- V1 分片上传和断点续传的最大文件规模目标是多少？
- Artifact / Recipe 何时需要独立 version tree 和 diff 视图？
- Artifact 生命周期和自动清理策略如何定义？

## Agent

- V1 Expert 模式是否允许用户手动编辑 JSON Plan 后再执行？
- V1 多模型路由按哪些任务类型拆分：Planner、Explainer、Report，还是按成本等级？
- V1 工具文档 RAG 使用 pgvector 还是 Qdrant？

## Materials Domain

- V2 VASP 输出优先解析 vasprun.xml、OUTCAR、XDATCAR 还是 DOSCAR？
- V1 代表结构聚类使用 composition embedding 还是 structure fingerprint？
- V1 首批高级工具优先实现 phonon、trajectory、RDF/XRD，还是 ML error-by-domain？
- V1/V2 外部生态集成优先级如何排序：Materials Project、OPTIMADE、AiiDA、atomate2，还是内部数据库 connector？
- 电子结构工具是否进入 V2 核心范围，还是作为专业插件优先接入？

## Security

- V1 组织级 BYOK 的继承、撤销和预算模型如何设计？
- V1 Prompt injection 模型辅助检测使用哪类评估集？
- V2 是否需要 gVisor / Firecracker / Kubernetes Jobs 等更强隔离？

## Implementation

- MVP 是否接受 `preview_png` 继续保持 optional，还是在 render-worker 里显式安装并管理 Kaleido/Chromium？
- ZIP 安全解包的 MVP 限制值如何定：最大文件数、最大展开大小、最大嵌套层级？
- EXTXYZ with lattice：已决定优先通过 ASE 解析后转 pymatgen Structure，不再单独实现轻量 parser。
- V1/V2 manifest 工具在进入可执行阶段前，是否要求先补齐与 MVP 同等级的 `additionalProperties=false` paramsSchema？
- 下一阶段实现 SSE 时需要选择与 `fastapi 0.115.x` / `starlette 0.46.x` 兼容的 SSE 方案；当前全局环境中的 `sse-starlette 3.4.1` 要求 `starlette>=0.49.1`，不能直接作为项目依赖锁定。
## 2026-07-04 Official pymatviz Examples Evidence Pack Follow-ups

- Source provenance still needs official commit pinning for a final publication-quality report. Current evidence marks `source_commit: unresolved` and `source_commit_status: TODO_PIN_BEFORE_FINAL_REPORT`.
- Official examples that require script/notebook execution remain `PARTIAL_PASS`; decide whether a future phase should build a controlled script/notebook import path or keep them as reference-only mappings.
- Composition and structure adapters exist, but Planner tool routing for official example workflows is not yet productized. Decide whether Phase 10 should add prompt/profile-based routing beyond `ml.basic_metrics`.
- Phonon, Brillouin zone, advanced MatterViz widgets, classification curves, and richer Plotly/table/report outputs remain future adapter/tool work.
