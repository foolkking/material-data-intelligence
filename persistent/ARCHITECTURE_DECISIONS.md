# ARCHITECTURE_DECISIONS

## ADR-092: Phase 10B should productize composition visualization before structure/physics adapters

### Context

Phase 10A-1 and Phase 10A-2 established a first official-example baseline for
table, general visualization, and safe composition summary adapters. The
official pymatviz benchmark pack is still only partially benchmark-ready: two
direct verified cases exist, while the remaining cases are extraction-required,
mapping-only, or future-scope.

The Tool Registry already contains broader composition, structure, and phonon
tool IDs, but registered tools are not equivalent to official browser/API
evidence. The next adapter phase needs a scope that is material-specific,
deterministic, and small enough to verify without new external dependencies or
fragile browser rendering.

### Decision

Use Phase 10B as a docs-only planning phase and recommend Phase 10B-1 for
composition visualization adapters:

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `composition.chem_sys_sunburst`
- `composition.formula_statistics`

Defer `structure.viewer_3d`, XRD, RDF, phonon, Brillouin zone, notebook
extraction, script execution, and external API workflows to later phases.

### Consequences

- The next implementation phase can deepen pymatviz-specific value without
  changing QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, live LLM
  gating, or frontend execution authority.
- Existing MVP composition tools can be hardened in place instead of duplicated
  under new tool IDs.
- Ward's direct verified composition column is the best first source of browser
  and API evidence; README periodic-table examples remain mapping references
  until real input data is available.
- Structure and physics adapters still matter, but require separate dependency,
  fixture, tolerance, and screenshot-stability planning.

## ADR-091: Phase 10A-2 evidence commits browser/API/artifact proof without making it a CI gate

### Context

Phase 10A-1 implemented the first table and visualization adapter batch for the
two `DIRECT_VERIFIED` official pymatviz cases. Unit, registry, planner-routing,
persisted execution, and frontend tests proved the adapters, but the phase did
not yet provide presentation-grade browser/API/artifact evidence for the new
outputs.

### Decision

Commit a project-local evidence pack under `docs/phase10a/browser_api_evidence/`
for the scoped first-batch scenarios:

- MatPES `viz.scatter`
- MatPES `viz.histogram`
- Ward `table.distribution_summary`
- Ward `viz.histogram`
- Ward `viz.correlation`
- Ward `composition.summary`

Each scenario stores redacted API captures, downloaded artifacts, screenshots,
execution logs, result summaries, artifact manifests, and an evidence manifest.
The evidence pack is documentation/demo evidence and is not a default CI gate.
Default CI continues to run unit, frontend, and service-backed integration tests
without real LLM calls.

### Consequences

- First-batch official direct-case adapter outputs now have auditable evidence
  beyond unit tests.
- Evidence remains scoped: it does not imply the other 59 official examples are
  verified.
- Secret scanning is required before commit; the evidence must not contain API
  keys, Authorization headers, bearer tokens, or raw secrets.
- The execution architecture remains unchanged: persisted AnalysisPlans still
  load through QueueWorkerRuntime and execute through Tool Registry + Adapter.
- Browser/API evidence can support demos and reports, but CI should not become
  dependent on screenshots or local browser state.

## ADR-090: Phase 10A-1 official examples add single-step table and visualization adapters

### Context

The official pymatviz benchmark pack has two `DIRECT_VERIFIED` direct-uploadable
cases: MatPES atomic energies and Ward metallic glasses. Phase 9B/9C evidence
proved the persisted execution path for `ml.basic_metrics` and
`table.numeric_summary`, but the benchmark contract preserves richer first
batch expectations such as scatter plots, histograms, distribution summaries,
correlation heatmaps, and safe composition summaries.

### Decision

Add first-batch tools as single-step registry-gated adapters:

- `table.distribution_summary`
- `viz.scatter`
- `viz.histogram`
- `viz.correlation`
- `composition.summary`

`viz` is a shared ToolDomain for general visualization artifacts that are not
specific to ML, composition, structure, or phonon domains. These adapters accept
normalized objects such as `ml_table`, emit named artifacts plus `summary.md`
and `recipe.json`, and expose strict params schemas through Tool Registry.

Mock Planner may route MatPES scatter/histogram prompts and Ward
distribution/correlation/composition prompts to these tools, but it still only
produces structured AnalysisPlan JSON. PlanValidator remains the boundary before
persistence, job creation, and enqueue.

### Consequences

- MatPES can be verified beyond metrics with `viz.scatter` and `viz.histogram`
  while preserving `ml.basic_metrics` for explicit PBE vs r2SCAN metric prompts.
- Ward can use table distribution and correlation tools without treating
  independent material properties as regression target/prediction pairs.
- `composition.summary` is safe partial support: it runs only when a stable
  formula/composition field exists and must not fabricate missing composition
  data.
- The Phase 8B persisted-plan execution contract is unchanged. QueueWorkerRuntime
  still loads persisted plans by `job.plan_id` and executes via Tool Registry +
  Adapter.
- The Phase 9D live LLM path is unchanged and remains gated outside default CI.
- Multi-step DAG workflows and broader official examples remain future phases.

## ADR-089: Live LLM params must satisfy Tool Registry paramsSchema before persistence

### Context

Phase 9D live verification proved that a real OpenAI-compatible provider can
return a syntactically valid AnalysisPlan with a valid tool ID but invalid
parameter names for that tool. In the observed live run, the provider selected
a registry-approved plotting tool but emitted aliases that did not match the
registered params schema. Letting such a plan persist would move the failure
from the planner boundary to adapter runtime.

### Decision

PlanValidator must validate each `AnalysisStep.params` object against the
selected registered tool's `paramsSchema` before any AnalysisPlan can be
persisted, bound to a job, or enqueued. Prompt guidance may list allowed
parameter names, but prompt wording is advisory only; the registry schema is
the enforcement boundary.

The live provider still only returns JSON AnalysisPlan. It does not execute
code, enqueue work directly, or call adapters. Valid plans continue to flow:

```text
Live provider JSON -> PlanValidator -> persisted AnalysisPlan -> jobs.plan_id
-> QueueWorkerRuntime -> Tool Registry -> Adapter -> Artifact/Result
```

### Consequences

- Invalid live-provider params fail before persistence/job/enqueue.
- Adapter runtime no longer has to be the first place that catches invalid
  step params for known tools.
- Tool Registry manifests remain the source of executable parameter contracts.
- Default CI remains real-LLM-free; live verification remains gated by
  `MDI_RUN_LLM_INTEGRATION=1`.
- Secret/API key values remain forbidden in prompts, plans, JobEvents,
  Artifacts, Reports, Recipes, screenshots, and exported evidence.

## ADR-088: Explicit planner provider config wins over environment defaults

### Context

Phase 9A introduced a gated OpenAI-compatible provider. Phase 9C added UI
provider configuration and Secret selection. The audit for Phase 9D found that
the UI correctly passed provider config to `/planner/jobs`, but the provider
resolver could let env model/timeout/token/temperature values override explicit
request config. The UI also showed the env-default provider status, which could
be confused with the current task provider selection.

### Decision

When a `PlannerUserConfig` is explicitly supplied by a request/UI path, its
model, timeout, max token, and temperature values win over env defaults. When
no `user_config` is supplied, the env-only path keeps reading `MDI_LLM_*` /
`OPENAI_*` for gated local live tests.

Add a no-network provider resolve API for the current UI/task configuration.
It reports whether the selected planner mode would use Mock Planner or a live
OpenAI-compatible provider, whether a selected secret exists, and the effective
model, without returning API keys or contacting the provider.

### Consequences

- UI-selected provider settings now match the provider used by `/planner/jobs`.
- The default env provider status remains available, but it is no longer the
  only status shown in the model dialog.
- Default CI remains safe because live LLM tests still require
  `MDI_RUN_LLM_INTEGRATION=1` and provider env.
- The execution boundary is unchanged: live provider output is still JSON
  AnalysisPlan only, validated before persistence and executed through
  QueueWorkerRuntime plus Tool Registry/Adapter.

## ADR-087: Phase 9C frontend baseline uses a top/left/main-tab AI assistant workspace

### Context

Phase 9B productized the Planner workspace, but its layout still carried the
old engineering lineage: left controls, central prompt/plan area, right
health/provenance/timeline, and bottom result tabs. The desired product
direction is an AI analysis assistant workspace that keeps context visible
without splitting execution process, conversation, and results across fixed
page columns.

The user explicitly rejected an independent right-side Result Inspector. Agent
process, conversation/Plan, and results must all live inside the main workspace
and be selected by tabs.

### Decision

The canonical frontend layout is now:

```text
Top global context bar:
  current dataset + model status + dataset/model dialogs + system settings

Left data-context viewer:
  resizable, collapsible, format-adaptive dataset/profile viewer

Main workspace:
  tabs = Agent 过程 / 对话与 Plan / 结果与导出
  only one main tab is visible at a time
```

`结果与导出` owns report summaries, 3D material views, metrics, table/numeric
summaries, Artifact Gallery, Recipe/provenance, report export, and artifact
downloads. These are not implemented as a persistent right-side panel.

`对话与 Plan` owns natural-language conversation chunks, Plan Preview,
validation chunks, and run-status chunks. Chunk selection drives the context
shown later in `结果与导出`.

`Agent 过程` owns structured JobEvent/ToolCall timeline display and safe
payload disclosure. It must not show hidden chain-of-thought, raw completions,
or secrets.

### Consequences

- Old right Agent panel and bottom result panel designs are legacy background,
  not the preferred Phase 9C implementation target.
- Frontend implementation should migrate toward `AIPlannerWorkspace`,
  `GlobalContextBar`, `DataContextViewer`, `MainWorkspaceTabs`,
  `AgentProcessTab`, `ConversationPlanTab`, and `ResultsExportTab`.
- The initial implementation baseline now applies this in `PlannerWorkbench`:
  dataset/model controls moved into top dialogs, the left panel is a
  resizable/collapsible viewer, and results are rendered only through the main
  `结果与导出` tab.
- This is a UI information-architecture decision only. It does not change
  AnalysisPlan schema, persisted plan loading, queue-worker semantics, Tool
  Registry, Adapter behavior, or provider security.
- Execution authority remains backend-owned:
  `/planner/jobs` -> PlanValidator -> persisted AnalysisPlan -> job.plan_id ->
  QueueWorkerRuntime -> Tool Registry -> Adapter.

## ADR-086: Ward-style tabular summaries use table.numeric_summary instead of regression metrics

### Context

The official Ward metallic glasses CSV can be uploaded and profiled as a table.
The previous demo path selected the first two numeric columns (`D_max` and
`dTx`) for `ml.basic_metrics`. That proved the execution chain but was not
semantically correct: those columns are independent material properties, not a
natural target/prediction pair.

### Decision

Add `table.numeric_summary` as a minimal MVP platform builtin tool. It accepts a
normalized DataFrame and emits descriptive table statistics as `table_json`
(`numeric_summary.json`), plus `summary_md` and `recipe_json` when requested.

Mock Planner may route explicit table-summary/Ward prompts to
`table.numeric_summary`; regression/comparison prompts such as MatPES PBE vs
r2SCAN still route to `ml.basic_metrics`.

### Consequences

- Ward browser evidence now summarizes `D_max` and `dTx` independently and
  reports categorical summaries for fields such as `composition` and
  `gfa_type`.
- The Phase 8B execution contract remains unchanged: plans are validated,
  persisted, bound through `jobs.plan_id`, loaded by QueueWorkerRuntime, and
  executed through Tool Registry + Adapter.
- Richer Ward visualizations such as composition heatmaps, element
  distributions, histograms/scatter plots, and richer report generation remain
  future work.

## ADR-085: Mock Planner may bind metric params from DataProfile but cannot execute or repair plans

### Context

The official pymatviz examples evidence pack exposed a Phase 9B demo blocker.
`matpes_atomic_energies_csv` uploaded and profiled successfully, but the Mock
Planner generated `ml.basic_metrics` params for `y_true` and `y_pred`. The
official CSV columns are `element`, `PBE`, and `r2SCAN`, so adapter execution
failed even though the plan passed schema and registry validation.

### Decision

Allow `MockLLMProvider` to use the supplied `DataProfile` when generating its
structured AnalysisPlan JSON. For `ml.basic_metrics`, it now selects explicit
target/prediction role columns first. If roles are absent but the table has at
least two numeric columns, it uses the first two numeric columns. Otherwise it
falls back to the previous `y_true` / `y_pred` defaults.

This is planner-side parameter selection, not execution repair. The provider
still returns JSON only. `/planner/jobs` still validates the plan before
persistence, stores the exact validated AnalysisPlan, binds it through
`jobs.plan_id`, and lets QueueWorkerRuntime load and execute it through Tool
Registry and Adapter.

### Consequences

- MatPES-style role-less numeric tables can complete in the demo workspace
  without requiring a special frontend override or deterministic fallback.
- The Phase 8B persisted-plan execution contract remains intact: the worker
  executes the persisted plan and still emits `plan.loaded`, `data.loaded`,
  ToolCall, Artifact, and JobEvent provenance.
- No Tool Registry manifest or adapter behavior changed.
- Future work remains for richer domain routing: composition/formula tables
  should steer to composition tools, and structure inputs should steer to
  structure tools when the profile and user intent indicate those domains.

## ADR-084: Queue workers load normalized dataset objects from persisted exports

### Context

ADR-083 closed the local in-memory demo gap by letting the API process auto-run
the default in-memory queue. That did not fully address out-of-process queue
workers: a Redis/RQ worker receives only `job_id`, so it cannot rely on the API
process' in-memory Phase2 dataset object store. The worker must be able to load
normalized dataset inputs from persisted metadata and artifact storage.

### Decision

Add a durable worker object-store resolver. `DurableObjectStoreResolver` reads
dataset `metadata.normalizedExports` from the repository, loads each exported
object and its metadata from configured ArtifactStorage, and reconstructs the
conventional execution refs used by plans and adapters: `ml_table`,
`structures`, and `formulas`.

`run_queued_job(job_id)` is now settings-driven. It creates SQLAlchemy
repositories from `DATABASE_URL`, artifact storage from
`MDI_ARTIFACT_BACKEND` / `MDI_ARTIFACT_ROOT`, installs the durable resolver,
and then calls `QueueWorkerRuntime.handle_job(job_id)`. The PostgreSQL planner
runtime construction path uses the same resolver and storage configuration.

The resolver is input binding only. It does not modify the persisted
AnalysisPlan, select tools, enqueue work, or execute outside the Tool Registry
and Adapter path.

### Consequences

- A Redis/RQ worker running in a separate process can execute persisted plans
  for datasets whose normalized exports are stored in repository metadata and
  ArtifactStorage.
- Worker execution remains auditable through `data.loaded`, `plan.loaded`,
  ToolCall, Artifact, Result, and JobEvent provenance.
- Local and service-backed Phase 8B semantics remain intact: persisted
  `job.plan_id` is still the execution source and one-step persisted plans still
  execute as exactly one ToolCall.
- The remaining production hardening item is the upload service boundary: the
  worker can consume persisted normalized exports, but the upload path still
  needs a production implementation that writes dataset/profile/export metadata
  directly through SQL and MinIO/S3 instead of the Phase2 local runtime.

## ADR-083: Local planner demo jobs may auto-drain only on the in-memory queue path

### Context

Phase 8B established the production contract: `/planner/jobs` persists the
validated `AnalysisPlan`, creates a `jobs.plan_id` binding, and enqueues only
`job_id`; a worker later loads the persisted plan and executes it through Tool
Registry and Adapter. Phase 9B productized the workspace, but full local demo
testing exposed two practical gaps: default in-memory dev jobs could remain
queued without a separate worker process, and uploaded dataset objects were not
available to the default queue worker by `dataset_id`.

### Decision

The default in-memory planner runtime may auto-drain a just-enqueued job only
when all of the following are true: the default in-memory repositories are in
use, the default in-memory queue backend is in use, no custom planner runtime
was injected, and no Redis queue URL is configured. In that case, the route
still creates the persisted plan/job first and then calls
`QueueWorkerRuntime.handle_job(job_id)`, so execution still flows through the
worker path rather than through a frontend shortcut or deterministic fallback.

`QueueWorkerRuntime` now accepts an object-store resolver. The default local
resolver loads uploaded/demo dataset objects from the Phase2 runtime by
`dataset_id`, emits a `data.loaded` JobEvent, then loads `job.plan_id` and the
persisted `AnalysisPlan`. Planner preview/jobs also prefer the real Phase2
`DataProfile` when available, and uploaded dataset plans are rejected before
persistence when required normalized inputRefs are missing or unresolved.

### Consequences

- Local demos can complete an enqueued planner job without requiring a second
  worker process, which makes the Phase 9B workspace demonstrable from a single
  API process.
- The production Redis path is preserved: when a Redis queue is configured, the
  route enqueues only `job_id` and does not auto-run the worker.
- Injected test runtimes keep their previous behavior, preserving Phase 8B
  regression tests for enqueue semantics and persisted-plan execution.
- Dataset binding is explicit and auditable through `data.loaded`,
  `plan.loaded`, ToolCall, Artifact, and Result provenance.
- Out-of-process Redis workers still need durable normalized-object loading for
  uploaded datasets; the resolver seam creates the extension point but does not
  replace future production storage hardening.

## ADR-082: Phase 9B productizes Planner UX without moving execution authority to the frontend

### Context

Phase 8B/8C/8C-P1 proved persisted-plan execution and frontend provenance, and
Phase 9A added a gated OpenAI-compatible provider path. The Planner page was
still too close to an engineering debug panel for demos: English labels,
developer fields, broad empty placeholders, limited data-context entry, and no
product-level provider/secret/error/result workflow.

### Decision

Phase 9B moves the Planner workspace to a demo-ready product interface while
keeping execution authority in the backend. The frontend now has a default
Chinese i18n layer with an English toggle, productized data/provider/prompt/run
panels, runtime health display, SSE timeline, grouped artifacts, report/recipe
summary, error explanations, and user/developer mode layering.

The backend adds only support/read APIs and safe provider-test helpers:
runtime health, dataset detail/demo/profile support, provider catalog/status,
provider test, and Secret UX metadata. Provider tests resolve credentials by
`secretId` on the server and return redacted results. They do not persist raw
prompts or completions, execute tools, enqueue jobs, or write artifacts.
Browser access is enabled through an explicit CORS allow-list for local/demo
web origins. Runtime health is a read-only observability surface: configured
database, Redis, and MinIO/S3 backends are checked with light probes, and
failures are reported as redacted component status rather than as raw
connection strings or credential-bearing provider errors.

Planner job creation remains owned by `/planner/jobs`: provider output must
parse as JSON, construct an `AnalysisPlan`, and pass PlanValidator before any
plan can be persisted, job created, or queue message sent. The frontend does
not write `analysis_plans`, compute authoritative plan hashes, directly
enqueue work, or treat deterministic fallback as the normal product path. If
validation fails, the rejected raw plan is not echoed back to the caller.

### Consequences

- Phase 9B improves demo readiness and operator clarity without weakening the
  Phase 8B persisted-plan execution contract.
- API keys remain out of localStorage/sessionStorage, Secret list responses,
  JobEvents, Artifacts, AnalysisPlans, Results, and provider-test errors.
- The UI can present mock and OpenAI-compatible modes, but default CI remains
  real-LLM-free and live LLM verification is still gated by Phase 9A env.
- The demo dataset/profile path is backend-generated through the Phase2
  runtime; it is labeled as demo data and is not a fake frontend success path.
- Phase 9B follow-up keeps CORS, runtime health, and i18n cleanup as
  product-readiness/support changes; they do not move execution authority to
  the frontend or weaken the Tool Registry boundary.
- Production secret encryption/KMS, multi-step DAG/data-dependency execution,
  worker supervision/dead-letter policy, and advanced material viewer polish
  remain future work.

## ADR-081: Phase 9A real LLM provider is gated and cannot bypass validation or persistence

### Context

Phase 8B and Phase 8C completed persisted-plan execution and frontend
provenance display using mock/deterministic-safe planner providers. The next
increment needs a real OpenAI-compatible provider path without making default
tests or CI depend on external LLM services and without weakening the Phase 8B
validation/persistence/queue boundary.

### Decision

Phase 9A adds a gated OpenAI-compatible planner provider. The default provider
remains mock/deterministic-safe. The real provider is selected only through an
explicit provider request or `MDI_LLM_PROVIDER=openai_compatible` and is
configured by `MDI_LLM_BASE_URL`, `MDI_LLM_API_KEY`, `MDI_LLM_MODEL`,
`MDI_LLM_TIMEOUT_SECONDS`, `MDI_LLM_MAX_TOKENS`, and
`MDI_LLM_TEMPERATURE`.

The provider uses an OpenAI-compatible chat completion request and asks for a
JSON object response. Raw prompts and raw completions are not persisted by
default. Missing API keys, unsupported providers, HTTP errors, network errors,
timeouts, and malformed responses are converted to safe provider failures that
do not include API keys.

All provider output still passes through JSON parsing, `AnalysisPlan` schema
construction, and PlanValidator. `/planner/jobs` only persists the exact
validated plan, creates a job, and optionally enqueues `job_id` after validation
success. Provider failure or validation failure remains an all-or-nothing
no-op: no plan, no job, no enqueue.

A `llm_integration` pytest marker covers live provider smoke testing, but it is
skipped unless `MDI_RUN_LLM_INTEGRATION=1` and required provider env are set.

### Consequences

- Default unit tests and default CI remain real-LLM-free.
- Fake-transport tests prove the OpenAI-compatible provider success/failure
  contract without external network calls.
- Phase 8B execution semantics are preserved: valid plans still flow through
  persisted AnalysisPlan storage, QueueWorkerRuntime, Tool Registry, and
  Adapter execution.
- API keys must not appear in AnalysisPlans, JobEvents, Artifacts, Results,
  provider errors, or test output.
- Live LLM verification is optional/gated and was not claimed locally without
  configured provider env.
- Production secret encryption/KMS, multi-step DAG execution, worker
  supervision/dead-letter policy, and advanced material viewer polish remain
  future work.

## ADR-080: Phase 8C-P1 uses read-only SSE and data-context selection to close UX compliance gaps

### Context

The Phase-by-phase code acceptance audit found no Phase 8C P0 blocker, but it
identified P1 gaps against the frontend workspace docs: the timeline needed a
primary SSE/EventSource path, report/recipe summary needed its own panel, and
dataset/profile entry needed a selectable data-context workflow rather than raw
ID fields only.

### Decision

Phase 8C-P1 adds a read-only planner JobEvent SSE replay endpoint and makes the
Planner workbench use EventSource as the primary timeline transport. Polling is
kept as a fallback only. The SSE endpoint replays persisted JobEvents and does
not mutate plans/jobs, enqueue work, execute tools, or call deterministic
fallback planning.

The UI now separates `Artifact Gallery` from `Report / Recipe Summary`. The
Report/Recipe panel presents result summary, report artifacts, recipe artifacts,
artifact references, `planId`, `planHash`, and persisted-plan provenance.

The Planner workbench now includes an API-backed Dataset/Profile selector using
the existing `/datasets` and `/datasets/{dataset_id}/profile` read endpoints.
Manual ID fallback remains available when discovery/profile reads are
unavailable. The UI does not invent fake dataset/profile records.

### Consequences

- Phase 8B execution semantics remain unchanged: persisted plans still execute
  through QueueWorkerRuntime, Tool Registry, and Adapter paths.
- `/planner/jobs` remains the only frontend job-creation path and still owns
  validation, persistence, job creation, and enqueue semantics.
- The frontend has a docs-compliant SSE timeline path while retaining a robust
  fallback for local/dev environments.
- Phase 8C-P1 is accepted after implementation commit `4d0c241` passed GitHub
  Actions run `28664159687`; the service-backed integration job reported 19
  passed, 0 skipped, and 0 failed.
- True LLM integration, multi-step DAG scheduling, production secret encryption,
  and worker supervision/dead-letter policy remain future work.

## ADR-079: Phase 8C exposes persisted plan provenance through the Planner UX

### Context

Phase 8B made persisted AnalysisPlans executable by the queue runtime, but the
frontend still did not expose the product workflow. Users could not create a
Planner Job from the UI, inspect the validated persisted plan, or see evidence
that the worker loaded `job.plan_id` instead of a request-body or deterministic
fallback plan.

### Decision

Phase 8C adds a Planner workbench as the frontend entry point for persisted
AnalysisPlan jobs. The frontend creates jobs only through `POST /planner/jobs`
and displays backend-returned `jobId`, `planId`, and `planHash`; it does not
write `analysis_plans`, enqueue queue messages, or compute an authoritative
plan hash client-side.

Read-only planner endpoints were added for persisted AnalysisPlan, planner job
detail, JobEvents, ToolCalls, Artifacts, and result summary. These endpoints are
display APIs only: they do not mutate plans/jobs, enqueue work, trigger
execution, or call deterministic fallback planning.

The UI treats `plan.loaded` as the primary runtime evidence for persisted-plan
execution. It displays `job.plan_id -> analysis_plans.id`, Tool Registry +
Adapter execution text, ToolCall/Artifact/Result plan provenance, and explicit
validation-failure messaging that no plan, job, or queue message was created.

### Consequences

- Phase 8B remains the execution baseline; QueueWorkerRuntime and
  AnalysisPlanRepository were not redesigned.
- Users can now inspect the persisted AnalysisPlan binding and plan provenance
  from the frontend.
- Validation failure no longer looks like a created or queued job in the UI.
- True LLM integration, DAG scheduling, production secret encryption, worker
  supervision/dead-letter policy, and advanced material viewer polish remain
  future phases.
- Phase 8C is accepted/frozen after implementation commit `9967c5b` passed
  GitHub Actions run `28646226271`; the service-backed integration job reported
  19 passed, 0 skipped, and 0 failed.

## ADR-078: Phase 8B persists validated plans and queue workers load by job_id

### Context

Phase 8A proved exact LLM plan execution only inside the in-memory
`Phase2ProductRuntime`. The remaining production gap was durable handoff:
there was no `analysis_plans` table, no `jobs.plan_id`, and the Redis-capable
`QueueWorkerRuntime` could not reconstruct the plan from `job_id` alone.

### Decision

Validated `AnalysisPlan` JSON is persisted before job creation in a new
`analysis_plans` table. Jobs reference it with nullable `jobs.plan_id`.
`plan_hash` is `sha256(canonical_json(AnalysisPlan))`; raw prompts and raw
LLM completions are not stored by default, and credential-like params are
rejected before persistence.

`POST /planner/jobs` now follows:

`provider -> PlanValidator -> save AnalysisPlan -> create Job(plan_id) -> optional enqueue(job_id)`

Validation failure is an all-or-nothing no-op: no plan, no job, no enqueue.
The route does not synchronously execute production work.

`QueueWorkerRuntime.handle_job(job_id)` now treats persisted plan loading as
the main path: load Job, read `plan_id`, load the persisted plan, reconstruct
`AnalysisPlan`, execute exact `steps`, and write ToolCall, JobEvent, Artifact,
and final Job status with plan provenance. Caller-supplied `plan` remains a
dev/test fallback only for jobs without a persisted plan.

### Consequences

- A persisted 1-step plan produces exactly 1 ToolCall, with `toolId` and
  `stepId` copied from the persisted plan.
- `build_phase2_plan` is not used when a job already has `plan_id`.
- Tool Registry + Adapter remain the only execution path.
- Phase 8B was frozen at commit `962c429` after GitHub Actions run
  `28631817086` proved PostgreSQL + Redis + MinIO integration with 19 passed,
  0 skipped, and 0 failed.
- Phase 8C frontend Planner UX may start after that frozen baseline.

## ADR-077: Phase 8A — the validated LLM plan becomes the job's execution plan

### Context

Phase 7 validated LLM AnalysisPlans but discarded them: `/planner/jobs`
created a job that ran the deterministic `build_phase2_plan`, not the LLM
plan. This was honestly documented but left the core "LLM → execution" loop
open.

### Decision

`Phase2ProductRuntime.create_job` accepts an optional `analysis_plan`. When
provided, that EXACT validated plan becomes the job's execution plan — the
runtime iterates its `steps` through the unchanged Tool Registry + Adapter
path (`run_tool_call_job`). The deterministic `build_phase2_plan` is used only
as a fallback when no plan is provided. A separate `execute` flag supports
planned-only job creation (persist plan, run nothing).

The bridge does NOT mutate or auto-repair the validated plan. If the plan's
steps are not runnable (e.g. unresolvable inputRefs), the ToolCall fails
honestly — the bridge never silently rewrites the plan.

### Consequences

- A 1-step LLM plan produces exactly 1 ToolCall, not the deterministic 5
  (proven by `test_runtime_executes_exact_provided_plan_one_tool_call`).
- The deterministic planner remains a valid fallback/test baseline.
- Execution is still local/in-memory; Redis QueueWorkerRuntime + PostgreSQL
  plan persistence is the next integration step (OPEN_QUESTIONS).
- Tool Registry + Adapter remain the only execution gate; PlanValidator still
  rejects invalid/unknown/V1-V2 plans before any job is created.

## ADR-074: Phase 7 LLM Planner emits AnalysisPlan JSON only; never executes

### Context

Phase 7 introduces an LLM-backed planner that converts a natural-language
request into an executable analysis plan. Letting the LLM execute Python,
shell, or call pymatviz directly would break the security, auditability, and
reproducibility guarantees the platform is built on.

### Decision

The LLM may ONLY emit a structured `AnalysisPlan` JSON object. It cannot
execute code, cannot call pymatviz/MatterViz directly, and cannot bypass the
Tool Registry. The `LLMPlannerProvider` protocol returns a
`PlannerRawResponse` (raw JSON / text only). The plan must pass `PlanValidator`
before any job is created. Execution still flows through the existing
`ToolExecutionRequest` -> Tool Registry -> Adapter path.

### Consequences

- The LLM is a planner, not an executor. All executable capability remains
  behind the Tool Registry + Adapter boundary.
- Non-JSON or markdown-wrapped completions are parsed defensively
  (`_parse_llm_json` strips fences, returns None on failure) so a bad
  completion is rejected with a structured error, never an unhandled exception.
- A deterministic planner (`build_phase2_plan`) is preserved as a
  fallback/test baseline.

## ADR-075: Phase 7 PlanValidator is strict — no auto-repair

### Context

An LLM can produce plans that are malformed, reference unknown tools, use
V1/V2 tools, duplicate step IDs, or smuggle credentials into params. A planner
that auto-repairs and then executes such plans would silently run mutated,
unreviewed instructions.

### Decision

`PlanValidator.validate_plan()` runs in strict mode only. It rejects:
non-dict input, schema-invalid plans, empty steps, duplicate step IDs, unknown
tool IDs, non-MVP tools, unknown artifact types, unknown input ref types, and
credential-like keys in params. On any failure it returns structured errors
and the caller MUST NOT create a job, enqueue work, or run an adapter.
Automatic repair is explicitly deferred (recorded in OPEN_QUESTIONS).

### Consequences

- Invalid plans never reach execution.
- `/planner/preview` and `/planner/validate` never create jobs.
- `/planner/jobs` only creates a job after validation succeeds.
- Note: in Phase 7 the created job currently runs the deterministic plan, not
  the validated LLM plan (the LLM→execution wiring is deferred — see
  OPEN_QUESTIONS). This is an honest boundary, not a completed closed loop.

## ADR-076: BYOK Secret uses a SecretStore abstraction; InMemory only for dev/test

### Context

BYOK requires storing user LLM API keys. Plaintext keys must never leak into
prompts, logs, JobEvents, Artifacts, Recipes, Reports, or API responses.
Production needs envelope encryption, but the encryption infrastructure (KMS /
key management) is not available in this phase.

### Decision

Introduce a `SecretStore` protocol with three implementations:
`InMemorySecretStore` (dev/test only — holds plaintext in memory),
`EncryptedSecretStore` (placeholder, raises NotImplementedError). The list API
returns only metadata (id, provider, created_at) — never the plaintext value.
`get_secret` returns the value only for internal use (e.g. constructing an LLM
request). Redaction helpers scrub credential keys/values from any text or
params destined for logs.

### Consequences

- The API surface never returns plaintext secret values.
- Production deployment is blocked on implementing real envelope encryption in
  `EncryptedSecretStore` (recorded in OPEN_QUESTIONS).
- Tests use `InMemorySecretStore`; no real API key is required.

## ADR-073: Phase 6 uses opt-in integration markers for live service verification

### Context

Phase 5 wired PostgreSQL/Redis/MinIO runtime configuration, but the actual live service smoke was not yet integrated into the test suite. Phase 6 needs to verify that the PostgreSQL repository, Redis queue backend, and MinIO artifact storage work against real Docker-backed services without breaking the Docker-free unit test baseline or adding mandatory infrastructure dependencies.

### Decision

Add 18 integration smoke tests under `tests/test_phase6_integration.py` gated behind `@pytest.mark.integration`. All tests skip cleanly when `MDI_RUN_INTEGRATION` is not set to `1` or when individual services (PostgreSQL, Redis, MinIO) are not reachable. Each test uses helper functions (`_pg_url()`, `_live_redis_client()`, `_minio_storage()`) that call `pytest.skip()` on connection failure.

Integration test categories:
- Docker compose services reachability (1 test): verify PG/Redis/MinIO are alive.
- Alembic live migration (1 test): real `alembic.command.upgrade(alembic_cfg, "head")` against live PG with downgrade+reupgrade cycle and index existence checks.
- PostgreSQL repository live (6 tests): CRUD, rollback, status transitions.
- PostgreSQL JobEvent seq live (3 tests): monotonic, advisory lock, concurrent seq.
- Redis queue live (2 tests): enqueue/dequeue, worker runtime with live repos.
- Queue retry idempotency (2 tests): duplicate job handle, crash+retry.
- MinIO live (2 tests): put/get/exists/signed-url.
- Service-backed product-loop (1 test): PG repos + queue + storage + real Tool Registry + BasicMetricsAdapter.

Keep default unit tests Docker-free. Integration tests can be run with:
```bash
MDI_RUN_INTEGRATION=1 DATABASE_URL=... REDIS_URL=... python -m pytest -q -m integration
```

### Consequences

- Phase 6 can verify live service interaction on any machine with Docker without breaking the existing CI/development workflow of `python -m pytest -q`.
- Each integration test is individually skippable, so partial infrastructure failures don't block the entire suite.
- The `MDI_RUN_INTEGRATION` flag and per-service health checks provide clear error messages instead of opaque connection errors.
- CI pipeline must eventually add a service-backed job that starts Docker services and runs the integration suite.

### Alternatives Considered

- Make Docker mandatory for all tests: rejected because ordinary development and CI smoke tests must remain reproducible without external services.
- Use testcontainers-python: rejected to keep dependency surface minimal and avoid Python testcontainer provisioning complexity.
- Skip only on `MDI_RUN_INTEGRATION` flag without per-service checks: rejected because individual service failures (e.g., Redis down but PG up) would produce confusing errors.

## ADR-072: Phase 5 wires production runtime infrastructure without changing tool scope

### Context

Phase 4 hardened repository persistence with Alembic metadata, transaction
boundaries, status machines, idempotent ToolCall writes, idempotent Artifact
metadata writes, and per-job JobEvent seq cursors. Phase 5 needs to connect
that foundation to real runtime infrastructure while keeping the project out of
real LLM execution, V1/V2 tool expansion, full auth, frontend redesign, and
Kubernetes/Ray/autoscaling.

### Decision

Support standard runtime variables (`DATABASE_URL`, `POSTGRES_*`, `REDIS_URL`,
and `MINIO_*`) while preserving the existing `MDI_*` aliases. Alembic uses the
configured runtime database URL when present and keeps the SQLite ini fallback
when no runtime database is configured.

Keep PostgreSQL as the fact source for Job, ToolCall, Artifact metadata, and
JobEvent state. Add a small SQLAlchemy engine/repository-factory helper for
runtime wiring instead of letting services create ad hoc engines.

Use Redis/RQ as the first queue-backed runtime adapter, but keep an
`InMemoryQueueBackend` for deterministic tests and no-Redis local runs.
`QueueWorkerRuntime` receives `job_id`, loads repository state, executes tool
steps through the existing Tool Registry + Adapter path by default, writes
ToolCall status, appends JobEvents, records Artifact metadata, and converges on
stable records under duplicate enqueue or retry.

For PostgreSQL JobEvent seq allocation, use a transaction-scoped advisory lock
keyed by `job_id` before calculating `seq = max(seq) + 1`. SQLite keeps the
existing in-process lock for unit tests. The unique `(job_id, seq)` constraint
remains the final data-integrity guard.

Extend `S3CompatibleArtifactStorage` so it remains a Phase 4 metadata mapping
when no client is configured, but becomes a live MinIO/S3 client when a
boto3-compatible client or credentials are supplied. Artifact bytes live in
MinIO/S3; metadata remains in PostgreSQL.

### Consequences

- Phase 5 can run default unit tests without Docker while exposing opt-in
  PostgreSQL/Redis/MinIO integration points.
- Worker retries can be tested without a real broker and can later be dispatched
  through Redis/RQ with the same handler semantics.
- SSE resume semantics remain based on `(job_id, seq)` and are compatible with
  PostgreSQL multi-worker allocation.
- Live signed URLs are available for configured MinIO/S3 storage, while local
  and placeholder mapping behavior remains stable for no-client environments.

### Alternatives Considered

- Make Docker services mandatory for all tests: rejected because ordinary
  development and CI smoke tests must remain reproducible without external
  services.
- Adopt Celery immediately: deferred because Phase 5 only needs a minimal
  queue-backed worker and the docs already allow lightweight Redis-backed
  choices before production orchestration.
- Store artifact bytes in PostgreSQL: rejected because the architecture keeps
  object bytes in MinIO/S3 and only metadata/provenance in PostgreSQL.
- Use only a unique constraint and retry loop for JobEvent seq allocation:
  deferred in favor of an explicit per-job transaction lock, which is easier to
  reason about for SSE cursor monotonicity.

## ADR-071: Phase 4 hardens persistence with transactions, status machines, and idempotent writes

### Context

Phase 3 introduced repository abstractions, SQLAlchemy persistence smoke tests,
JobEvent seq cursors, SSE smoke streaming, and artifact storage mapping. The
next step is to make that foundation production-migration-ready without adding
real LLM calls, V1/V2 tools, Celery/Ray/Kubernetes, full auth, frontend rewrites,
or live S3/MinIO clients.

### Decision

Add an Alembic baseline entrypoint and a PostgreSQL-oriented Phase 4 baseline
revision while keeping SQLAlchemy Core metadata compatible with SQLite tests.

Add `RepositorySession`, `UnitOfWork`, and `RepositoryFactory` as the explicit
transaction boundary for SQLAlchemy repositories. A unit of work owns one
connection and one transaction; commit, rollback, and close are explicit and
covered by tests.

Centralize Job and ToolCall status validation. Job supports `created`, `queued`,
`running`, `partial_success`, `completed`, `failed`, `cancel_requested`, and
`cancelled`. The queued production path is `created -> queued -> running`; the
local synchronous worker may continue to use `created -> running` to preserve
Phase 2/3 behavior. ToolCall supports `planned`, `running`, `completed`,
`failed`, and `skipped`; legacy `created` ToolCall inputs normalize to
`planned` at repository boundaries.

Make worker-facing writes idempotent at the repository layer. ToolCalls reuse a
stable row by `(job_id, step_id)` or `(job_id, idempotency_key)`. Artifacts reuse
a stable row by `(job_id, storage_key, sha256)`. JobEvents keep `(job_id, seq)`
as the SSE resume cursor; SQLite tests use an in-process lock, and production
PostgreSQL must use row/advisory locking or an equivalent per-job allocation
strategy before multi-worker deployment.

### Consequences

- Phase 4 can be handed off as a migration-ready persistence baseline while the
  existing Phase 2/3 local loop remains stable.
- Failed transactions roll back repository writes without corrupting committed
  Artifact metadata.
- Worker retries can converge on stable ToolCall and Artifact records instead
  of producing uncontrolled duplicates.
- The next runtime phase must wire these boundaries into real PostgreSQL
  sessions, queue workers, and object-storage clients.

### Alternatives Considered

- Introduce Celery/PostgreSQL/MinIO runtime wiring now: rejected because this
  phase is limited to production persistence hardening, not infrastructure
  rollout.
- Keep status changes ad hoc in each repository: rejected because legal
  transitions need one auditable implementation and consistent tests.
- Use only database unique constraints for idempotency: rejected because
  repository behavior should return stable records and remain testable before
  production database deployment.

## ADR-070: Phase 3 introduces repository and artifact-storage abstractions before production infrastructure

### Context

Phase 2 proved the local product loop with in-memory state and local files. The
next backend layer needs durable semantics for projects, datasets, jobs, job
events, tool calls, artifacts, recipes, reports, SSE resume cursors, and
object-storage mapping. The user explicitly excluded real LLM integration,
V1/V2 tool expansion, Celery/Ray/Kubernetes, full auth, production PostgreSQL
wiring, live S3/MinIO clients, and frontend rewrites from this phase.

### Decision

Add repository interfaces for Project, Dataset, DataProfile, Job, JobEvent,
ToolCall, Artifact, Recipe, and Report records. Keep InMemory implementations
for the existing Phase 2 runtime, and add SQLAlchemy Core implementations that
can run against SQLite tests while remaining oriented toward PostgreSQL metadata
and migration drafts.

`job_events` keeps `(job_id, seq)` as the resume cursor. Every append assigns a
monotonic per-job seq, and the in-process implementations guard seq allocation
with locks so acceptance tests cannot produce duplicate seq values. Query APIs
expose `list_events_after_seq(job_id, after_seq)` plus
`GET /jobs/{job_id}/events?after_seq=N`. Add `GET /jobs/{job_id}/stream` as a
plain FastAPI `StreamingResponse` SSE smoke endpoint over the current local
event store.

Add `ArtifactStorage` as a separate boundary from artifact metadata. The local
implementation maps storage keys to files and computes content metadata. The
S3/MinIO-compatible implementation is a metadata/signed-url placeholder until
the project adopts a live object-storage client and access-control policy.

### Consequences

- Phase 3 creates a migration-ready persistence boundary without destabilizing
  the accepted Phase 2 loop.
- Cursor semantics can be tested before concurrent workers and production SSE
  backpressure are introduced.
- Artifact metadata can carry storage provider, bucket, storage keys, content
  type, sha256, size, created time, and preview mapping independently from the
  current local file store.
- Future Celery/PostgreSQL/MinIO work must wire these interfaces with real
  transactions, idempotent worker writes, auth checks, and live signed URLs.

### Alternatives Considered

- Wire Celery, PostgreSQL, and MinIO immediately: rejected because this phase
  only asks for the persistence abstraction and handoff foundation.
- Replace Phase 2 InMemory runtime wholesale: rejected because Phase 2
  acceptance must remain stable while durable repositories are introduced.
- Add an SSE dependency: deferred because the current FastAPI/Starlette lock can
  smoke-test streaming with `StreamingResponse` without widening dependencies.

## ADR-069: Phase 2 uses an in-memory local product runtime before durable infrastructure

### Context

Phase 2 needs an executable product loop across dataset upload, parsing,
DataProfile generation, deterministic planning, Job/ToolCall execution,
Artifact export, JobEvents, Recipe, Report, and API query routes. The goal is
to prove the workflow boundary without prematurely adding PostgreSQL, Redis,
Celery, MinIO, real LLM providers, full auth, or V1/V2 tools.

### Decision

Add `apps/api/mdi_api/phase2_runtime.py` as the Phase 2 runtime. It uses:

- `InMemoryJobStore` for jobs, tool calls, and events.
- `LocalFileArtifactStore` over `LocalArtifactExporter` output for artifact
  metadata and content lookup.
- The existing parser/profile library for dataset understanding.
- A deterministic planner that emits an `AnalysisPlan` with 3-5 MVP tool calls.
- The existing controlled execution path:
  `ToolExecutionRequest` -> Tool Registry validation -> Adapter -> Artifact.

The Phase 2 API routes read and write this local runtime state. The route
contract is intentionally shaped so a later repository-backed implementation
can replace the in-memory store without changing the product flow.

### Consequences

- Phase 2 can be accepted with real local API calls and real adapter artifacts.
- No secrets, arbitrary code execution, or direct LLM tool execution are added.
- The runtime is not a production state store and must be replaced by durable
  repositories, queue workers, object storage, and access-control checks in a
  later phase.
- Frontend work remains out of scope for this round; API and tests prove the
  backend product loop.

### Alternatives Considered

- Add PostgreSQL/Celery/MinIO immediately: rejected for this round because the
  user explicitly requested the local in-memory runtime boundary first.
- Extend the Phase 1 demo runtime directly: rejected because Phase 2 needs API
  queryable project/dataset/job/artifact state, while Phase 1 remains an
  acceptance/demo fixture.

## ADR-068: Phase 1 acceptance uses a deterministic product-flow runtime

### Context

The docs/01 Phase 1 MVP acceptance criteria require an end-to-end product flow:
project creation, upload parsing, Data Profile, natural-language analysis request,
Analysis Plan summary, registry-approved Worker execution, artifacts, Recipe,
Report, and JobEvent progress display. The project does not yet have production
repositories, Celery workers, object-storage upload sessions, or a real LLM
planner wired into the API.

### Decision

Add a deterministic local Phase 1 runtime in `apps/api/mdi_api/phase1_demo.py`.
It is an acceptance/demo boundary, not a production shortcut. The planner reads
Data Profile + Tool Registry and emits an `AnalysisPlan`; it does not call a
real LLM and does not execute arbitrary Python. Tool execution still flows
through `run_tool_call_job()` -> `execute_tool_request()` -> Tool Registry
validation -> Adapter execution.

### Consequences

- Phase 1 product acceptance is now executable and covered by tests.
- The Agent contract remains intact: structured JSON plan only, no direct
  pymatviz/Python/shell execution.
- The runtime proves event and artifact semantics before durable repositories
  are implemented.
- Next-phase work must replace in-memory/demo storage with PostgreSQL,
  object storage, Celery, and durable SSE cursors.

### Alternatives Considered

- Mark Phase 1 as scaffold-only: rejected because docs/01 requires product-flow
  acceptance evidence.
- Wire a real LLM/API immediately: rejected for MVP acceptance because the
  planning boundary can be proven deterministically without adding secrets,
  provider variability, or network dependency.

## ADR-001：LLM 不直接执行任意代码

### Context

系统需要使用 LLM 根据自然语言和材料数据自动规划分析流程，但直接让 LLM 写 Python 并执行存在安全、稳定性、可审计性和复现风险。

### Decision

LLM 只生成结构化 JSON Plan。所有可执行能力必须通过 Tool Registry 暴露，并经过 Schema 校验、权限检查、资源限制和沙箱隔离。执行结果以 ToolCall、Artifact、Recipe、日志和报告形式保存。

### Consequences

- 系统更安全、可审计、可复现。
- Agent 输出更稳定，前端可以展示结构化过程。
- 需要维护 Tool Registry、Adapter、Schema、错误模型和工具版本。
- 灵活性低于任意代码执行，但更适合多用户科研平台。

### Alternatives Considered

- 让 LLM 直接写 Python 执行：灵活但危险，不适合作为默认平台能力。
- 完全不用 LLM：稳定但无法满足自然语言分析规划目标。
- 只做静态模板推荐：实现简单，但难以覆盖多样材料数据和科研问题。

## ADR-002：系统定位为平台，而不是 pymatviz 套壳

### Context

pymatviz、MatterViz 和 Plotly 提供关键可视化能力，但用户目标是围绕材料数据文件、自然语言需求、Agent、异步任务、Artifact、Recipe 和安全配置构建完整分析平台。

### Decision

pymatviz / MatterViz / Plotly 被定位为 Visualization Service 和 Tool Registry 下的工具能力。平台必须包含文件解析、Data Profile、Agent 编排、任务系统、Artifact 管理、Recipe 复现、用户配置和安全边界。

### Consequences

- 后续设计不能只围绕图表函数封装展开。
- 服务边界、数据库、任务队列、安全和前端工作台需要从 Phase 1 起同时考虑。
- Tool Adapter 设计需要兼顾材料对象标准化、参数校验、缓存和 Artifact 输出。

### Alternatives Considered

- 只封装 pymatviz 函数：开发快，但无法满足智能分析平台和可复现工作流目标。
- 直接做通用 BI：不具备材料对象、结构可视化和领域分析能力。

## ADR-003：项目按独立系统设计，同时保留 LabPilot 集成能力

### Context

系统目标已经明确为“自然语言 + 材料数据文件 -> 数据分析、Plotly/MatterViz 图表、3D 结构模型、过程展示和可复现 Artifact”。它可以成为 LabPilot 的子系统，但如果从一开始只作为内部功能开发，会限制权限、部署、任务队列、用户配置和 Artifact 管理边界。

### Decision

按独立系统设计核心架构：Project、Dataset、Job、ToolCall、Artifact、Recipe、Config、Secret、AuditLog 都作为系统级一等实体。后续可通过 API、SSO、嵌入式工作台或共享存储集成到 LabPilot。

### Consequences

- 架构设计必须包含独立登录/组织/项目/权限边界。
- 前端按完整材料分析工作台设计，而不是 LabPilot 中的单个页面组件。
- API 和 Artifact 格式需要稳定，便于未来独立部署、私有化部署或平台集成。

### Alternatives Considered

- 只作为 LabPilot 内部模块：集成快，但复用性、部署灵活性和产品边界较弱。
- 只做本地脚本/Notebook：适合研究探索，不适合多用户平台和可审计工作流。

## ADR-004：不 fork 大改 pymatviz，采用 Adapter 隔离上游变化

### Context

pymatviz 和 MatterViz 是关键能力来源，但平台需要更稳定的工具 Schema、输入校验、缓存、错误标准化、Artifact 输出和权限控制。直接 fork 并深度改造上游会增加维护成本。

### Decision

保持 pymatviz / MatterViz 作为底层依赖，新增 `pymatviz-agent-adapter` / Visualization Service 层：

- 统一函数签名。
- 定义 JSON Schema。
- 校验输入对象与参数。
- 注入平台默认配置。
- 标准化 Artifact 输出。
- 标准化错误和 Warning。
- 记录工具版本和执行环境。

### Consequences

- 平台稳定性不直接绑定上游内部实现。
- 后续可替换或补充自研工具、matminer、pymatgen、ASE、phonopy、Materials Project 等能力。
- Adapter 层需要持续维护工具映射和版本兼容表。

### Alternatives Considered

- 直接暴露 pymatviz API 给 Agent：简单但不安全、不稳定、不可审计。
- fork pymatviz：短期可控，但长期维护成本高。

## ADR-005：展示 Agent Timeline，而不是原始隐藏思维链

### Context

用户希望看到“系统如何绘制图表、每一步调用了什么”。这需要过程透明，但不应展示模型原始隐藏推理。

### Decision

前端展示结构化 Agent Timeline：

```text
Data Detection -> Data Quality -> Planning -> Tool Execution -> Artifact Generation -> Result Interpretation
```

每一步展示输入、选择理由、工具 ID、参数、状态、日志、Artifact 和 Warning。隐藏模型原始思维链，只展示产品化、可审计的过程记录。

### Consequences

- 满足用户对过程透明的需求。
- 避免泄漏隐藏推理、系统提示、密钥或不稳定内部推断。
- 需要在 JobEvent、ToolCall、Artifact 和 Report 中保存结构化过程数据。

### Alternatives Considered

- 展示完整模型思考链：不安全且不稳定。
- 只展示最终图表：缺少可审计性和科研复现价值。

## ADR-006：MVP 默认 Auto 模式，Guided / Expert 推迟到 V1

### Context

平台需要同时服务新手科研用户和高级材料信息学用户。完整支持 Auto、Guided、Expert 三种模式会增加 UI、权限、安全和 Recipe 编辑复杂度。

### Decision

MVP 默认采用 Auto 模式：系统基于用户自然语言、Data Profile 和 Tool Registry 自动生成 Analysis Plan，并向用户展示计划摘要、工具列表、关键参数和 warning。用户可以 Run、Regenerate 或 Cancel，但不直接编辑 JSON Plan。Guided 模式和 Expert Recipe/参数编辑器推迟到 V1。

### Consequences

- MVP 更快形成完整闭环。
- 用户仍能审查系统将要执行什么。
- 暂不暴露复杂 JSON Plan 编辑和受限 Python 代码编辑。

### Alternatives Considered

- MVP 直接支持 Expert 模式：高级但安全和体验复杂度过高。
- 完全不展示计划：简单但缺乏信任和可审计性。

## ADR-007：MVP 只支持登录用户，公开分享推迟到 V1

### Context

系统涉及材料文件上传、LLM Key、Artifact、Recipe 和执行日志。公开分享和游客访问会引入额外的权限、数据泄漏、链接过期和导出安全问题。

### Decision

MVP 默认只支持登录用户和项目成员访问。公开分享、匿名查看、报告公开链接和团队外分享推迟到 V1。

### Consequences

- MVP 权限模型更清晰。
- Secret、Artifact 和审计日志边界更容易控制。
- Phase 1 前端仍保留分享入口占位，但标记为后续能力。

### Alternatives Considered

- MVP 支持公开分享：产品传播更强，但安全边界更复杂。
- 完全不考虑分享：简单但不利于后续科研协作。

## ADR-008：前端产品形态是材料工作台，不是普通聊天页

### Context

用户需要同时管理文件、Data Profile、字段映射、图表、3D 模型、Agent 过程、日志、Artifact 和 Recipe。单一聊天界面无法承载这些信息。

### Decision

采用三栏式工作台 + 底部面板：

```text
左侧数据资产 / 中央可视化画布 / 右侧 Agent 面板 / 底部日志与 Artifact
```

自然语言输入是 Agent 面板的一部分，不是唯一界面。

### Consequences

- 前端设计从 Phase 3 起必须围绕工作台信息架构展开。
- 图表卡片、3D Viewer、Timeline 和 Artifact 面板都是一等产品对象。
- 用户能在同一界面完成数据理解、分析执行和结果复现。

### Alternatives Considered

- 纯聊天界面：开发快，但不适合材料数据分析工作流。
- 传统 BI 仪表盘：图表展示强，但缺少自然语言 Agent 和材料对象语义。

## ADR-009：MVP API 采用 FastAPI，保留 NestJS / LabPilot BFF 集成边界

### Context

平台核心执行能力依赖 pymatviz、pymatgen、ASE、phonopy、pandas、Plotly 等 Python 生态。若 MVP 主 API 采用 NestJS，再通过 RPC 调 Python 服务，会增加初期集成复杂度。

### Decision

MVP 采用 FastAPI 作为 API Gateway / Application Service，代码按 auth、project、data、agent、visualization、jobs、artifacts、config 等模块划分。前端使用 Next.js / React / TypeScript。未来如果需要深度集成 LabPilot 或 TypeScript BFF，可在 API Gateway 前增加 NestJS BFF，或将 FastAPI 作为后端材料服务。

### Consequences

- MVP 能更快连接 Python 材料工具链。
- API 合约仍需保持稳定，避免前端绑定内部模块。
- 后续引入 NestJS 不应改变 Artifact、Job、ToolCall、Recipe 的核心模型。

### Alternatives Considered

- NestJS 主 API + Python 微服务：类型系统和企业工程较强，但 MVP 复杂度更高。
- Next.js API routes 直接处理后端：不适合材料计算和异步 Worker 架构。

## ADR-010：MVP 采用模块化单体 + 独立 Celery Worker，而不是一开始微服务化

### Context

系统逻辑上需要 API、Data、Agent、Visualization、Worker、Artifact、Security 等边界，但 MVP 阶段过早拆成多个服务会增加部署、网络、鉴权、追踪和事务复杂度。

### Decision

MVP 部署采用 FastAPI 模块化单体 + 独立 Celery Worker Pool。逻辑服务边界在代码层保持清晰，Worker 按队列拆分为 parse、viz、render、llm、export。V1/V2 再按负载和团队边界拆分独立服务。

### Consequences

- MVP 运维简单，交付速度更快。
- 代码必须避免跨模块强耦合，为后续拆分服务保留接口。
- Worker 与 API 通过任务和数据库/对象存储交互，不直接共享运行时状态。

### Alternatives Considered

- 一开始微服务化：扩展性强，但对当前 0 到 1 阶段过重。
- 单进程同步应用：实现简单，但无法支撑材料解析、图表、3D 和 LLM 长任务。

## ADR-011：MVP 异步任务采用 Celery + Redis，复杂编排后续升级 Temporal

### Context

文件解析、Data Profile、LLM 规划、pymatviz 可视化、3D 渲染和报告生成都可能耗时。平台需要 Job Queue、Worker Pool、事件流、重试和超时控制。

### Decision

MVP 使用 Celery + Redis：Redis 作为 broker/cache/transient state，Celery workers 按任务类型分队列。若 Celery result backend 被启用，也只作为 Celery 技术实现细节，不作为业务事实源。系统通过 `jobs`、`job_events`、`tool_calls` 和 `artifacts` 表持久化真实状态。长流程、补偿、可恢复编排和跨服务 saga 后续可迁移 Temporal。

### Consequences

- MVP 技术栈成熟、实现成本低。
- Redis 故障不应导致持久化状态丢失。
- Phase 8 需要进一步定义 worker 并发、资源限制、重试、超时和可观测性。

### Alternatives Considered

- Dramatiq + Redis：更轻量，但生态和团队熟悉度需评估。
- Temporal：强工作流能力，但 MVP 学习和部署成本较高。
- 同步执行：不满足高并发和流畅展示目标。

## ADR-012：PostgreSQL 存元数据，S3/MinIO 存文件和 Artifact，Redis 存短期状态

### Context

平台会产生原始上传文件、标准化对象、Plotly JSON、HTML、PNG preview、MatterViz viewer、metrics/table、报告、Recipe、日志和审计事件。SVG/PDF 论文图导出进入 V1。不同数据有不同访问模式和大小。

### Decision

采用三层存储：

- PostgreSQL：用户、组织、项目、数据集、文件元数据、Data Profile、Job、JobEvent、ToolCall、Artifact、Recipe、Config、Secret 引用、AuditLog。
- S3/MinIO：原始文件、解析产物、Plotly/MatterViz Artifact、报告文件、导出文件。
- Redis：队列、缓存、短期状态、rate limit counters。

### Consequences

- 数据查询和权限控制集中在 PostgreSQL。
- 大文件和图表产物不会膨胀数据库。
- Artifact 访问必须通过元数据权限校验和签名 URL。

### Alternatives Considered

- 所有内容存 PostgreSQL：简单但不适合大 Artifact。
- 本地文件系统：开发方便，但不适合多 Worker、多实例和云部署。

## ADR-013：MVP 中 MatterViz 和重型 Plotly HTML 通过 sandboxed artifact iframe 展示

### Context

MatterViz / 3D viewer 和大型 Plotly HTML 可能包含复杂 JS、WebGL 状态和较大数据。如果直接嵌入主 React 树，可能影响页面性能、安全边界和错误隔离。

### Decision

MVP 优先将 MatterViz viewer、heavy Plotly HTML 和导出预览作为 Artifact 通过 sandboxed iframe 展示。轻量 Plotly JSON 可由 React 组件直接渲染。V1 再评估 native MatterViz / React 集成。

### Consequences

- 重图表不会阻塞主工作台 React 树。
- Artifact 可复现性更好，iframe 加载内容与保存产物一致。
- 需要处理 iframe 高度、自适应、全屏和权限策略。

### Alternatives Considered

- 全部直接 React 组件渲染：交互更深，但稳定性和隔离较弱。
- 全部静态图片：性能好，但失去交互价值。

## ADR-014：MVP Dashboard 使用固定响应式布局，拖拽布局推迟到 V1

### Context

用户需要稳定理解数据资产、图表、Agent 过程和 Artifact。MVP 若加入拖拽布局，会增加保存布局、冲突处理、响应式适配和测试复杂度。

### Decision

MVP 使用固定响应式布局：三栏工作台 + 中央多 Tab + 图表卡片网格。V1 再支持用户自定义 Dashboard 和拖拽布局。

### Consequences

- MVP 可快速交付清晰一致的工作台体验。
- 图表位置和文档截图更稳定。
- 高级用户的个性化布局需求推迟。

### Alternatives Considered

- MVP 支持拖拽：灵活但复杂。
- 单页长列表：简单但不适合多类型材料分析。

## ADR-015：Agent Plan 默认摘要展示，完整 JSON 可展开

### Context

完整 JSON Plan 对高级用户有价值，但对多数科研用户噪声较高。直接默认展示 JSON 会降低可读性。

### Decision

MVP 默认展示 Plan Summary：目标、工具、目的、关键参数、预计 Artifact 和 Warning。完整 JSON Plan、ToolCall 输入和参数放在可展开 Details 中。

### Consequences

- 默认体验更清晰。
- 高级用户仍可审查细节。
- 前端需要同时支持摘要视图和详情视图。

### Alternatives Considered

- 默认展示完整 JSON：透明但不友好。
- 完全隐藏 JSON：友好但可审计性不足。

## ADR-016：Code 面板展示脱敏复现代码和 Recipe，不展示 Worker 内部脚本

### Context

用户希望看到“绘制过程和代码”，但 Worker 内部执行脚本可能包含临时路径、内部实现细节或敏感上下文。

### Decision

Code 面板展示由 Tool Registry 生成的脱敏复现代码片段、工具调用伪代码和 Recipe JSON 摘要。不展示 Secret、用户 API Key、内部临时绝对路径或未经审查脚本。

### Consequences

- 满足科研复现和学习需求。
- 降低泄密和误导风险。
- Tool Adapter 需要维护可复现代码模板。

### Alternatives Considered

- 展示完整 Worker 代码：透明但安全风险高。
- 不展示代码：安全但削弱复现价值。

## ADR-017：MVP 上传采用对象存储预签名直传，分片/断点续传推迟到 V1

### Context

材料数据可能包含 ZIP、CIF 批量包和表格文件。让 API 进程直接承载文件流会影响并发和稳定性。分片上传可以改善大文件体验，但会增加前后端复杂度。

### Decision

MVP 使用对象存储预签名 URL 直传，并设置文件大小、类型和过期时间限制。分片上传、断点续传和上传加速推迟到 V1。

### Consequences

- API 服务不处理大文件流。
- MVP 实现简单且适合 Celery Worker 后续解析。
- 超大文件体验推迟优化。

### Alternatives Considered

- API multipart 表单上传：实现简单但 API 压力大。
- MVP 直接支持分片：体验好但复杂度高。

## ADR-018：Artifact 和 Recipe 使用不可变记录 + version 字段

### Context

图表和分析流程需要可复现。如果用户修改参数或重新运行，不应覆盖旧结果。

### Decision

MVP 中 Artifact、Recipe、Report 采用不可变记录。每次重跑或修改生成新记录，并使用 `version` 字段标识版本。复杂版本树、diff 和合并功能推迟到 V1。

### Consequences

- 历史结果可追踪。
- 实现比单独 version table 更简单。
- 后续如需版本树，可迁移到 `artifact_versions` / `recipe_versions`。

### Alternatives Considered

- 原地覆盖：简单但不可审计。
- 独立版本表：更规范但 MVP 复杂。

## ADR-019：权限模型采用组织 + 项目 RBAC

### Context

平台包含文件、Job、Artifact、Recipe、Secret、审计日志和导出。需要清晰的数据隔离和权限边界。

### Decision

采用组织 + 项目 RBAC：organization 是租户边界，project 是数据和任务边界。MVP 角色为 owner、admin、researcher、viewer。所有资源查询默认受 project scope 限制。

### Consequences

- 数据隔离清晰。
- Project Owner 可以管理成员、Secret 和配置。
- V1 可扩展到资源级权限和公开分享。

### Alternatives Considered

- 只有用户私有空间：简单但不支持团队协作。
- 细粒度 ACL 起步：灵活但实现复杂。

## ADR-020：API 错误采用统一 Problem Details 风格

### Context

前端需要一致处理上传失败、解析失败、计划校验失败、工具执行失败、Artifact 不存在和权限问题。

### Decision

API 错误统一返回 `code`、`message`、`details`、`request_id`。错误码按 Auth、Dataset、Agent、Tool、Artifact、System 分类。

### Consequences

- 前端可以按错误码展示可操作提示。
- 日志和审计可以通过 request_id 追踪。
- 后端模块需要维护统一错误码表。

### Alternatives Considered

- 返回自由文本错误：实现快但不可维护。
- 每个模块自定义错误格式：短期灵活，长期割裂。

## ADR-021：Agent 只能输出 JSON Analysis Plan，不能执行代码

### Context

平台需要 LLM 理解自然语言并规划材料分析，但任意代码执行会破坏安全、可审计和可复现目标。

### Decision

Agent 的可执行输出只能是 JSON Analysis Plan。Execution Controller 负责 JSON parse、Schema 校验、Tool Registry 校验、输入引用校验、权限/预算/资源校验，然后创建 ToolCall。LLM 输出的代码、shell 命令或未注册工具不得执行。

### Consequences

- 安全边界清晰。
- 可复现性强。
- 需要维护 Plan Schema、Validator 和 Tool Registry。

### Alternatives Considered

- LLM 直接写 Python：灵活但风险高。
- 只用固定模板：安全但智能性不足。

## ADR-022：MVP 使用单模型配置，不做自动多模型路由

### Context

多模型路由可以优化成本和质量，但会增加模型选择、评估、回退和审计复杂度。

### Decision

MVP 支持用户/项目配置一个默认 OpenAI-compatible provider/model。系统不做自动多模型路由。V1 再支持按任务类型路由 Planner、Explainer、Report 模型。

### Consequences

- MVP 实现简单。
- 审计和成本统计清晰。
- 高级模型路由优化推迟。

### Alternatives Considered

- MVP 多模型路由：灵活但复杂。
- 固定系统模型不可配置：简单但不符合 BYOK 目标。

## ADR-023：MVP 不做完整工具文档 RAG，使用版本化 Tool Registry 摘要

### Context

Agent 需要知道工具能力、输入、参数和输出。完整 RAG 系统需要文档索引、向量库、召回评估和引用管理。

### Decision

MVP 将当前 Tool Registry 的版本化摘要、工具说明和参数 Schema 注入 Planner 上下文，不做完整工具文档 RAG。V1 再引入 pgvector/Qdrant 形式的工具文档检索。

### Consequences

- MVP 依赖少。
- 工具上下文更可控。
- 工具数量增长后需要升级 RAG。

### Alternatives Considered

- MVP 做完整 RAG：扩展性好但实现成本高。
- 不给 Agent 工具说明：计划质量差。

## ADR-024：Prompt injection 进入 Timeline warning，并阻止高风险计划

### Context

上传文件、CSV 列名、用户 prompt 和旧报告都可能包含指令注入内容。系统必须把数据和指令分开处理。

### Decision

Prompt Guard 检测危险请求：索要 Secret、绕过 Tool Registry、执行 shell、读取任意路径、忽略系统策略等。可疑内容写入 Agent Timeline warning；高风险内容使计划 validation failed，不创建 ToolCall。

### Consequences

- 用户能看到为什么系统拒绝或降级任务。
- 防护逻辑可审计。
- 需要维护规则和后续模型辅助检测。

### Alternatives Considered

- 静默忽略：用户难以理解。
- 完全相信用户输入：安全风险不可接受。

## ADR-025：MVP 工具参数 Schema 手写维护，V1 再评估半自动生成

### Context

pymatviz 函数参数多，直接暴露完整签名不适合 Agent 调用。自动提取签名可以减少维护，但需要处理类型、默认值、领域语义和安全限制。

### Decision

MVP 为白名单工具手写 Tool Schema，并用测试覆盖参数校验和 Adapter 行为。V1 再评估从 pymatviz 函数签名、docstring 或类型注解半自动生成 Schema。

### Consequences

- MVP Schema 更可控、更安全。
- 维护成本可接受，因为 MVP Tool Set 较小。
- 工具数量增长后需要自动化辅助。

### Alternatives Considered

- 自动暴露全部 pymatviz 函数：风险高且对 Agent 不友好。
- 只硬编码 UI，不建 Schema：无法支撑 Agent 和 Recipe。

## ADR-026：Plotly 工具必须输出 figure.json，并保证 MVP 交互展示路径

### Context

Plotly HTML 适合展示，但不利于后续重渲染、样式调整、复现和二次导出。

### Decision

所有 Plotly Adapter 必须输出 `figure.json`。每个需要在前端交互展示的 MVP Plotly Adapter，必须至少提供一种交互展示产物：优先 `figure.html`，或由前端直接渲染 `plotly_json`。MVP 推荐同时生成 `figure.html` 和 `preview.png`；`svg/pdf` 进入 V1 论文图导出链路。

### Consequences

- Artifact 可复现性更强。
- 前端可选择直接渲染 JSON 或加载 HTML iframe。
- 导出服务可以基于 JSON 重新生成图片。

### Alternatives Considered

- 只保存 HTML：展示方便但复现弱。
- 只保存 PNG：性能好但失去交互。

## ADR-027：MatterViz 工具输出 viewer.html + metadata.json，snapshot 可选

### Context

MatterViz/Widget 的运行时状态不等同于普通 Plotly Figure。MVP 必须保证交互查看和元数据检索；截图预览需要浏览器渲染 Worker，不能作为首版硬依赖。

### Decision

MVP 中 MatterViz Adapter 必须输出 `viewer.html`、`metadata.json` 和 `recipe.json`，可选输出 `snapshot.png` 与 `structure.json`。前端通过 sandboxed iframe 加载 viewer。

### Consequences

- 3D Viewer 可交互、可审计、可复现。
- snapshot 可用于 Dashboard 卡片，但不是 MVP 阻塞项。
- metadata 可用于报告和搜索。

### Alternatives Considered

- 强制生成 snapshot：首版会引入浏览器截图 Worker、沙箱和资源管理复杂度。
- 直接序列化 widget 内部状态：上游兼容风险高。

## ADR-028：Phonon / trajectory 高级工具推迟到 V1，MVP 只保留扩展点

### Context

MVP 需要保证结构数据和预测结果 CSV 两条核心路径闭环。phonon、trajectory、VASP、LAMMPS 工具重要但输入多样、解析复杂。

### Decision

MVP Tool Set 不包含 phonon 和完整 trajectory 工具，只保留 Tool Category、Schema 扩展点和文档设计。V1 再实现 phonon band/DOS 和 trajectory viewer。

### Consequences

- MVP 聚焦。
- 数据管线仍需预留 phonon/trajectory object types。
- V1 可以在不改 Agent 架构的情况下增加工具。

### Alternatives Considered

- MVP 同时实现 phonon/trajectory：专业性更强但范围过大。
- 完全不设计扩展点：后续架构改动大。

## ADR-029：Data Profile 必须由确定性解析管线生成，Agent 不直接猜文件内容

### Context

材料文件和表格数据复杂，LLM 直接阅读或猜测文件内容会导致不稳定、不可审计和安全风险。

### Decision

上传文件先经过 Format Detector、Parser Registry、Object Normalizer、Profile Builder 和 Quality Checker。Agent 只能读取 Data Profile、字段映射和 normalized object metadata 进行规划。

### Consequences

- Agent 计划更稳定。
- Data Profile 成为分析事实来源。
- 需要维护解析器和 profile schema。

### Alternatives Considered

- LLM 直接读文件：灵活但不可靠。
- 用户手动填写全部 metadata：准确但体验差。

## ADR-030：MVP 不执行 phonon 分析，保留识别和 Schema 扩展点

### Context

phonopy.yaml、band.yaml、DOS 等声子数据专业性强，解析和图表需要额外适配。MVP 已聚焦结构和 ML 预测结果。

### Decision

MVP 不提供 phonon band/DOS 执行工具。Data Pipeline 保留 phonon 文件识别、object type 和 profile 扩展点；V1 实现解析和工具。

### Consequences

- MVP 范围可控。
- 后续接入 phonon 不需要重构 Tool Registry。
- 用户上传 phonon 文件时可以提示“已识别，V1 支持分析”。

### Alternatives Considered

- MVP 支持 phonon：专业性强但拖慢核心闭环。
- 完全忽略 phonon：后续扩展成本高。

## ADR-031：VASP 输出和 LAMMPS dump 推迟到 V2

### Context

VASP 和 LAMMPS 输出种类多、文件大、上下文依赖强。过早支持会显著增加解析和质量检查复杂度。

### Decision

MVP 和 V1 优先结构文件、表格、trajectory、phonon。VASP 输出和 LAMMPS dump 推迟到 V2，Phase 7 只定义 future extension。

### Consequences

- MVP/V1 聚焦。
- Parser Registry 仍保留扩展点。
- 用户体验中需要明确 unsupported/future extension 状态。

### Alternatives Considered

- MVP 解析 VASP：适合计算材料用户，但范围过大。
- 完全不规划 VASP/LAMMPS：不符合长期专业平台目标。

## ADR-032：代表性 3D 结构 MVP 使用规则采样，聚类代表点推迟到 V1

### Context

用户希望生成几个代表性 3D 模型。聚类代表点需要 composition embedding、投影和距离度量，依赖更多工具链。

### Decision

MVP 使用规则采样：覆盖主要 chemical systems、小/中/大 atom count、异常结构优先，默认 3-8 个代表结构。V1 引入 composition/structure embedding 聚类代表点。

### Consequences

- MVP 可解释、实现简单。
- 代表性不如聚类严谨。
- 后续可替换为聚类策略而不改变前端流程。

### Alternatives Considered

- MVP 聚类选点：更科学但依赖更多工具。
- 用户手动选择：控制强但自动化不足。

## ADR-033：MVP 使用 SSE 推送 JobEvent，WebSocket 推迟到 V1

### Context

MVP 任务进度主要是服务端到前端的单向事件流。WebSocket 支持双向交互和协作，但运维和状态管理更复杂。

### Decision

MVP 使用 SSE 提供 `/jobs/{job_id}/events?cursor=...` 事件流，支持断线重连和 cursor 补齐。WebSocket 推迟到 V1，用于多人协作、presence、实时评论和双向控制。

### Consequences

- MVP 实现简单，和 `job_events` 表天然匹配。
- 前端可渐进展示 Artifact。
- 双向实时协作能力后移。

### Alternatives Considered

- MVP WebSocket：能力更强但复杂度更高。
- 前端轮询：实现简单但延迟和负载较差。

## ADR-034：Worker 按任务类型拆分队列

### Context

解析、LLM、可视化、渲染和导出任务的资源特征不同。如果混在一个队列，容易互相阻塞。

### Decision

MVP 使用 Celery 队列：`parse`、`profile`、`llm`、`viz`、`render`、`export`。不同 Worker Pool 可独立设置并发、超时和资源限制。

### Consequences

- render-worker 不会阻塞 parse-worker。
- LLM 限速和预算可单独控制。
- 运维需要监控每个队列。

### Alternatives Considered

- 单队列：简单但容易阻塞。
- 一开始 Kubernetes Jobs / Ray：扩展强但 MVP 复杂。

## ADR-035：PostgreSQL 是任务状态事实源，Redis 只做 broker/cache/短期状态

### Context

Redis 适合作为 broker 和缓存，但不应承担长期可审计状态。平台需要回放任务、审计工具调用和恢复 Worker 崩溃。

### Decision

`jobs`、`job_events`、`tool_calls`、`artifacts` 写 PostgreSQL。Redis 用于 Celery broker、短期 cache、rate limit counters 和 transient worker state。若 Celery result backend 被启用，也不作为业务事实源。

### Consequences

- 任务状态可恢复、可审计。
- Redis 故障不会导致历史状态丢失。
- 写入事件需要注意 PostgreSQL 压力和索引。

### Alternatives Considered

- Redis 作为唯一状态源：快但不可审计。
- 只写日志文件：查询和前端回放困难。

## ADR-036：大数据图表和 3D 模型默认启用降采样与 LOD

### Context

Plotly 和 WebGL 不能无限制渲染超大散点、超大结构或长 trajectory。直接加载会导致页面卡死。

### Decision

MVP 默认按规模启用降采样、density/hexbin、后端预聚合和 3D LOD。Artifact metadata 必须记录采样方法、原始规模和渲染规模。

### Consequences

- 前端展示更流畅。
- 用户需要看到采样说明，避免误解。
- 高精度完整渲染需要用户手动触发或进入 Expert/V1 能力。

### Alternatives Considered

- 全量渲染：简单但不可扩展。
- 只展示静态 summary：稳定但交互价值不足。

## ADR-037：Artifact、Recipe、Report 默认不可变，重跑生成新版本

### Context

科研分析需要可审计和可复现。若图表或 Recipe 原地覆盖，后续无法追踪报告所依据的具体参数和数据版本。

### Decision

MVP 中 Artifact、Recipe、Report 默认不可变。编辑、重跑或导出变化会生成新记录和新 `version`，并保留 `source_job_id`、`source_plan_id` 或 `source_recipe_id`。

### Consequences

- 历史分析可追踪。
- 存储会增长，需要后续生命周期策略。
- V1 可加入 diff 和版本树。

### Alternatives Considered

- 原地覆盖：简单但破坏复现。
- 一开始做完整版本树：强大但 MVP 复杂。

## ADR-038：Report Markdown 是 canonical，HTML 是派生产物，PDF 推迟到 V1

### Context

报告需要可读、可编辑、可版本化和可导出。HTML 适合展示，PDF 适合发布但生成链路更复杂。

### Decision

MVP 以 `report.md` 为 canonical，`report.html` 为前端展示派生产物。PDF 导出推迟到 V1。

### Consequences

- 报告源文件易于 diff 和复现。
- 前端仍可展示 HTML。
- 正式论文/归档 PDF 功能后移。

### Alternatives Considered

- HTML canonical：展示方便但不利于版本 diff。
- MVP 支持 PDF：用户价值高但导出链路复杂。

## ADR-039：MVP 不支持公开分享，只支持项目成员访问和授权导出

### Context

Artifact 可能包含未发表材料数据、模型结果和结构文件。公开链接会引入权限、撤销、过期和数据泄漏风险。

### Decision

MVP 不支持公开分享链接。Artifact、Report、Recipe 只对项目成员开放；授权用户可生成 export package 下载。公开分享、匿名报告和外部协作者访问推迟到 V1。

### Consequences

- MVP 安全边界更清晰。
- 团队内部协作可用。
- 对外传播和评审分享能力后移。

### Alternatives Considered

- MVP 支持公开链接：便利但安全风险高。
- 禁止导出：安全但科研使用价值不足。

## ADR-040：Job export package 异步生成，且必须脱敏

### Context

导出包可能包含多个图表、3D viewer、报告、Recipe 和 manifest，生成过程可能较慢且需要过滤敏感内容。

### Decision

Export package 作为异步任务生成。导出内容包含 Artifact、Recipe、Report、analysis_plan 和 manifest，不包含 Secret、内部绝对路径、隐藏思维链或未授权原始文件。

### Consequences

- 大导出不会阻塞 API。
- 导出结果可审计。
- 需要维护 manifest 和脱敏规则。

### Alternatives Considered

- 同步打包下载：简单但容易超时。
- 导出完整工作目录：复现强但泄密风险高。

## ADR-041：MVP Worker 沙箱采用 Docker/容器隔离，进程级隔离不足

### Context

平台需要解析用户上传文件并运行材料科学 Python 库。仅靠进程级隔离无法可靠限制文件系统、资源和网络访问。

### Decision

MVP Worker 在 Docker/容器化沙箱中执行，每个 job 使用独立临时目录、CPU/内存/超时限制、受控挂载和默认禁用外部网络。LLM worker 仅允许访问配置的 provider endpoint。

### Consequences

- 安全边界更强。
- 部署复杂度高于进程级隔离。
- V2 可升级到 Kubernetes Jobs 或更强隔离运行时。

### Alternatives Considered

- 进程级隔离：实现简单但风险高。
- Firecracker/gVisor 起步：安全强但 MVP 运维复杂。

## ADR-042：MVP 支持用户级 BYOK，组织级共享 Key 推迟到 V1

### Context

BYOK 对高级用户重要，但组织级共享 Key 涉及继承、撤销、审计、预算和成员访问控制。

### Decision

MVP 支持用户级 BYOK 和系统托管 Key。LLM Secret 按 job runner 解析：优先使用运行者自己的 BYOK，其次使用项目允许的系统 provider profile，最后使用部署级系统托管 Key。项目配置不能直接绑定另一个成员的用户级 BYOK 引用。组织级共享 Key 和组织级预算池推迟到 V1。

### Consequences

- MVP Secret 模型更简单。
- 用户自己控制自己的 Key。
- 多人项目中不会隐式借用 Owner 的个人 Key。
- Recipe 不保存具体 SecretRef，只保存 provider 能力需求。
- 团队统一 Key 管理能力后移。

### Alternatives Considered

- MVP 组织级共享 Key：团队体验好但权限复杂。
- 不支持 BYOK：实现简单但不满足长期目标。

## ADR-043：Secret 使用 envelope encryption，明文不进入日志、prompt、Artifact 或导出包

### Context

平台会处理 LLM Key、Materials Project Key、OPTIMADE endpoint credential 等敏感信息。

### Decision

Secret Service 使用 envelope encryption。数据库只保存加密引用和 metadata。明文只在 Worker 调用外部服务时短暂解密，并且不得写入 prompt、日志、JobEvent、Artifact、Recipe、Report 或 export package。

### Consequences

- Secret 泄漏风险降低。
- 调试时不能依赖日志查看 Key。
- 需要密钥轮换和审计机制。

### Alternatives Considered

- 明文存储：不可接受。
- 仅环境变量：不支持用户级 BYOK。

## ADR-044：Prompt injection MVP 使用规则检测 + 上下文隔离 + Plan Validator

### Context

用户 prompt、CSV/JSON 文本、旧报告和文件 metadata 都可能包含恶意指令。

### Decision

MVP 使用规则检测、上下文隔离和 Plan Validator 防护 prompt injection。可疑事件进入 Timeline warning 和 audit log；高风险计划阻止执行。模型辅助检测和测试集推迟到 V1。

### Consequences

- MVP 可控可解释。
- 防护不依赖另一个模型。
- 复杂攻击检测能力后移。

### Alternatives Considered

- 模型辅助检测起步：更灵活但增加成本和不确定性。
- 只靠系统提示：防护不足。

## ADR-045：插件默认无网络、无 Secret、无 shell，必须显式声明能力

### Context

专业材料扩展需要插件化，但插件可能带来供应链、数据访问和执行风险。

### Decision

插件默认禁用，项目管理员启用。插件 manifest 必须声明工具、资源、网络、Secret 和 shell 需求。默认无网络、无 Secret、无 shell。所有插件工具必须通过 Tool Registry 和沙箱执行。

### Consequences

- 插件扩展边界清晰。
- 管理员可审查插件能力。
- 高权限插件需要额外审批流程。

### Alternatives Considered

- 插件完全信任：扩展快但风险高。
- 不支持插件：安全但专业扩展能力不足。

## ADR-046：MVP 实现顺序按“数据闭环优先于高级功能”

### Context

系统范围覆盖前端、后端、Agent、材料解析、Tool Registry、异步任务、安全和 Artifact。若先做高级工具或复杂协作功能，会拖慢核心闭环。

### Decision

MVP 实现顺序固定为：pymatviz Capability Inventory & Adapter Baseline -> repo scaffold -> packages/schemas -> Tool Registry manifest loader -> BaseToolAdapter -> MVP 前 3 个 Adapter -> Data Pipeline -> Job Queue + SSE -> Artifact Service -> Agent JSON Plan + Validator -> 前端三栏工作台 -> 补齐 10 个 MVP 工具。

### Consequences

- 每个里程碑都能形成可验证增量。
- 高级材料工具、公开分享、PDF、RAG、Expert 模式推迟到 V1/V2。
- 开发过程优先保证端到端闭环，而不是局部功能深挖。

### Alternatives Considered

- 先做完整前端：可演示但无真实数据闭环。
- 先做完整工具库：工具强但缺少平台能力。

## ADR-047：专业材料领域扩展单独成文，但不改变 MVP 实现顺序

### Context

目标文件清单要求覆盖材料结构扩展、计算材料扩展、声子/电子结构扩展、机器学习材料扩展、生成材料评估、Materials Project / OPTIMADE / AiiDA / atomate2 扩展和插件机制。原设计已在 Phase 6、7、10、12 分散覆盖这些方向，但缺少一个集中面向领域扩展的长期设计文件。

### Decision

新增 `docs/11_MATERIAL_DOMAIN_EXTENSIONS.md` 作为领域扩展补充文件。它不改变 Phase 11 `docs/12_MVP_ROADMAP.md` 的编号和 MVP 实现顺序。阶段归属统一为：MVP 聚焦结构数据和预测结果 CSV；V1 接入 phonon band/DOS、trajectory viewer、RDF/XRD、spacegroup、composition clustering 和 ML error-by-domain；V2 接入 VASP/LAMMPS、电子结构、生成材料评估、外部数据库和插件市场。

### Consequences

- 专业材料扩展从分散说明变成集中设计，后续实现更容易追踪。
- Roadmap 仍保持“数据闭环优先于高级功能”。
- Tool Registry、Parser Registry、Plugin Manager 和 Security Layer 的扩展边界更清晰。

### Alternatives Considered

- 不新增领域扩展文件：文件数量少，但不满足目标清单，且长期扩展信息分散。
- 将领域扩展并入 Roadmap：会让 Roadmap 过长，也混淆开发计划与架构能力设计。

## ADR-048：docs/ 和 persistent/ 必须进入 Git 版本管理

### Context

本项目的核心资产是阶段化设计文档和持久化进度文件。若 `docs/` 与 `persistent/` 被 `.gitignore` 排除，后续 Coding Agent、团队成员和实现阶段都会丢失设计基线。

### Decision

`.gitignore` 不忽略 `docs/` 与 `persistent/`。设计文档、进度文件、ADR、任务看板和共享 Schema 都进入 Git。

### Consequences

- 新会话可以从仓库直接恢复上下文。
- 设计变更可审计。
- 团队协作有统一基线。

## ADR-049：统一 ArtifactType、DisplayTarget、ToolCategory 和 ToolDomain

### Context

Agent、Tool Registry、Artifact Service 和前端曾分别定义 `html`、`plotly_html`、`png`、`matterviz_snapshot` 等类型，容易导致 Schema 校验和前端渲染分叉。

### Decision

新增 `docs/13_SHARED_SCHEMA_SPEC.md` 作为跨模块类型基线。`ArtifactType`、`DisplayTarget`、`ToolCategory`、`ToolDomain`、`InputRef`、`DataProfile` 子类型、`ToolExecutionRequest`、`VisualizationRecipe` 等共享类型都以该文件为准。产物字段统一命名为 `artifactTypes`，不再使用“format”语义表达业务产物。

### Consequences

- 后续可从共享 JSON Schema 派生 TypeScript 和 Python Pydantic model。
- 减少前后端和 Worker 的重复类型定义。
- 插件扩展也必须遵守同一分类和领域模型。

## ADR-050：ToolInputSchema 使用 inputOptions 表达 OR 输入

### Context

许多 pymatviz / 平台工具支持多种输入形式，例如 formula column、Composition[]、Structure[] 或 element-value mapping。旧 `requiredObjectTypes` 容易被理解为全部输入都必需。

### Decision

Tool Registry 的输入 Schema 使用 `inputOptions: ToolInputOption[]` 表达多输入方案 OR 关系，并支持 `periodicity` 约束。

### Consequences

- `ptable_heatmap`、`chem_sys_treemap`、`structure_3d` 等工具可以准确描述多种输入。
- Plan Validator 能选择具体 input option 并给出可解释错误。
- plain XYZ 与周期结构工具的边界可被 Schema 表达。

## ADR-051：MVP table/metrics artifact 是一等产物

### Context

平台不是只画图，还要保存模型指标、离群样本、解析失败文件、质量问题和字段映射结果。若这些只在报告文本里出现，前端展示、复现和审计都会变弱。

### Decision

`metrics_json`、`table_json`、`table_csv`、`quality_issues_json` 进入统一 `ArtifactType`，MVP 工具 `ml.error_distribution`、`ml.basic_metrics`、`ml.outlier_table` 必须产出结构化指标或表格。

### Consequences

- 前端可以独立展示 outlier table、failed files、quality issues。
- Report Agent 有机器可读依据。
- Recipe 重跑可复现中间结构化结果。

## ADR-052：plain XYZ 不进入周期性结构工具，除非有 lattice

### Context

plain XYZ 通常没有晶格信息，不能专业上等价于周期晶体结构。把它直接交给 XRD、RDF、周期配位或结构质量工具会产生误导。

### Decision

plain XYZ 解析为 `Atoms` / molecule-like object；只有包含 lattice 的 EXTXYZ 或可明确标准化为周期 `Structure` 的对象才能进入 `periodic_required` 工具。

### Consequences

- 避免专业语义错误。
- Tool Registry 可通过 `periodicity` 明确输入要求。
- 前端可以把非周期对象展示为 basic geometry / composition preview。

## ADR-053：MVP MatterViz snapshot 可选，viewer.html + metadata.json 为必需

### Context

稳定生成 `snapshot.png` 需要浏览器渲染、截图 Worker、沙箱和资源管理。MVP 的核心价值是交互式 viewer 和可复现 metadata。

### Decision

MatterViz Adapter MVP 必须输出 `viewer.html`、`metadata.json`、`recipe.json`；`snapshot.png` 和 `structure.json` 为可选产物。V1 再稳定多角度截图和论文风格导出。

### Consequences

- MVP 复杂度降低。
- 3D Viewer 主路径仍然完整。
- 后续 render-worker 可逐步增强。

## ADR-054：Redis 不作为任务事实源，PostgreSQL 是唯一状态源

### Context

Redis 适合 broker/cache/transient state，但任务平台需要可恢复、可审计和可查询的状态源。若把 Celery result backend 当事实源，会和 PostgreSQL 状态冲突。

### Decision

PostgreSQL `jobs`、`job_events`、`tool_calls`、`artifacts` 是任务事实源。Redis 只做 broker、cache、rate limit 和短期状态。Worker 完成状态必须写入 PostgreSQL。

### Consequences

- SSE cursor、审计和任务恢复都有稳定来源。
- Redis 丢失不会丢任务历史。
- Worker 需要幂等写入和状态比较更新。

## ADR-055：用户级 BYOK 按 job runner 解析，不写入 Recipe

### Context

多人项目中，如果项目配置直接引用 Owner 的个人 Key，会产生权限继承、撤销和重跑语义问题。

### Decision

LLM 执行配置按 job runner 解析，优先使用运行者自己的 BYOK，其次项目允许的系统 provider profile，再使用部署级系统 Key。Recipe 不保存具体 SecretRef，只保存 provider 能力需求和模型类别。

### Consequences

- Owner 离开项目或撤销 Key 不会造成隐式 Key 共享。
- Recipe 更可迁移。
- V1 组织级 BYOK 可在此基础上扩展。

## ADR-056：V1 phonon 优先支持 phonopy.yaml + band.yaml，DOS 第二批

### Context

Phonon 数据格式多，全部首批支持会扩大 V1 范围。声子 band 是材料动力学稳定性分析的高频入口。

### Decision

V1 phonon 第一批优先支持 `phonopy.yaml` + `band.yaml` 到 `phonon.band`，DOS 文件作为第二批接入 `phonon.dos`。

### Consequences

- V1 phonon 路线更明确。
- Tool Registry 可以先固化 band path。
- DOS 不被遗忘，但不阻塞首批 phonon 能力。

## ADR-057：V1 composition clustering 默认 Magpie + PCA baseline，UMAP 可选

### Context

UMAP 对非线性分布有价值，但依赖和参数敏感度更高。MVP/V1 初期需要稳定、快速、依赖轻的 baseline。

### Decision

V1 composition clustering 默认 `Magpie + PCA baseline`，UMAP 作为高级可选投影。

### Consequences

- 默认结果稳定、可复现、速度快。
- 高级用户仍可选择 UMAP。
- Data Profile 和 Recipe 可记录 embedding/projection 参数。

## ADR-058：pymatviz 作为 primary visualization kernel

### Context

当前项目的核心目标是“pymatviz 能力抽象 + 材料数据智能分析 + 交互式可视化工作台”。已有架构定义了 Tool Registry、Adapter、Artifact、Recipe、Agent JSON Plan 和前端三栏工作台，但缺少一份明确的 pymatviz 原始能力到平台工具 ID 的能力清单与 manifest 基线。

### Decision

本项目以 `janosh/pymatviz` 作为材料可视化主内核，不 fork 修改 pymatviz，而是通过 Tool Registry + Adapter 抽象其能力。

正式实现时，首批 Tool Registry 来源为：

- `tool_registry/pymatviz_manifest.yaml`
- `tool_registry/matterviz_manifest.yaml`
- `tool_registry/platform_builtin_manifest.yaml`

所有 pymatviz / MatterViz / Plotly custom / platform builtin 能力必须先进入 capability inventory 或 manifest，再被 Agent 通过 `tool_id` 选择。Agent 只能生成 JSON Analysis Plan，不直接执行任意 Python 或调用原始 pymatviz 函数。

### Reasons

- pymatviz 已经覆盖材料信息学中的周期表、组成、结构、声子、RDF/XRD、ML 评估等可视化能力。
- 平台需要让 LLM 安全调用这些能力，因此必须引入 manifest、schema、adapter 和 artifact 标准化。
- 直接暴露 pymatviz 函数给 LLM 不安全、不稳定、不可审计。

### Consequences

- 所有 pymatviz 能力必须先进入 capability inventory。
- 所有可执行能力必须注册到 manifest。
- Agent 只能选择 Tool Registry 中的 tool_id。
- Adapter 实现必须记录 source package、source function/class、implementationSource、版本和 Artifact provenance。

## ADR-059：Milestone 0/1 代码采用 packages-first 共享库结构

### Context

当前阶段需要先打通 Tool Registry、共享 Schema、Adapter 和 Artifact Exporter。API、Worker 和前端尚未进入完整实现；若把 Adapter 直接放入某个 Worker 目录，后续 API 校验、测试、Job Worker 和 Recipe 重跑都会重复依赖封装。

### Decision

Milestone 0/1 采用 packages-first 结构：

- `packages/schemas` 保存 JSON Schema、TypeScript 类型和 Python/Pydantic 类型。
- `packages/tool-registry` 保存 manifest loader 和 Registry 查询 API。
- `packages/adapters` 保存 `BaseToolAdapter`、adapter registry 和 pymatviz/MatterViz adapter。
- `packages/artifact-core` 保存本地 Artifact Exporter。
- `apps/api`、`apps/web`、`services/workers` 先作为服务壳，后续从这些共享包导入能力。

### Consequences

- Tool Registry -> Adapter -> Artifact 的核心链路可以先被单元测试覆盖。
- 后续 API、Worker 和前端不会各自复制 schema/adapter 逻辑。
- 与 Roadmap 的建议目录保持一致，但将可复用代码放在 `packages/`，服务运行入口留给下一阶段。

## ADR-060：Data Pipeline 先实现库层闭环，再接上传服务和异步 Job

### Context

Data Profile 必须在 Agent 规划前由确定性程序生成。当前尚未实现上传服务、对象存储、Job Queue 和 Worker，但 Adapter 测试已经需要真实结构和表格对象作为输入。

### Decision

Milestone 2 先在 `packages/material-parsers` 实现本地库层：

- `detect_format()` 负责格式识别。
- `parse_file()` / `parse_dataset()` 负责将本地文件解析为 normalized object draft。
- `build_data_profile()` 负责生成轻量 `DataProfile`、quality issues 和 recommended tasks。
- CIF/POSCAR/CSV/JSON limited 首批可解析；plain XYZ 先识别为非周期边界但不进入周期结构工具；ZIP 和完整 EXTXYZ 标准化推迟到下一步。

### Consequences

- 后续 API、Worker 和测试可以复用同一套确定性解析逻辑。
- Agent 仍只读取 DataProfile，不直接猜测文件内容。
- 本阶段不声称完成生产上传/对象存储链路；normalized object 当前是 draft，后续由 Artifact/Object Storage 服务持久化。
- plain XYZ 的 MVP 库层语义是解析为非周期 `Atoms`，并以 quality warning 标记其不能进入 `periodic_required` 结构工具；它不是周期 `Structure`，也不应被 `structure.structure_3d` 等工具误用。

## ADR-062：EXTXYZ with lattice 通过 ASE 解析后转 pymatgen Structure

### Context

MVP 需要支持基础 XYZ/EXTXYZ 边界。plain XYZ 没有 lattice，必须保持非周期；但包含 `Lattice=` 的 EXTXYZ 文件应尽量复用成熟解析器，而不是手写轻量 parser。

### Decision

`detect_format()` 先识别 `.extxyz` 扩展名；`parse_file()` 使用 ASE 读取 EXTXYZ，再在 cell volume 有效时通过 `AseAtomsAdaptor` 转成 `pymatgen.Structure`。ZIP 容器解包采用路径安全检查，非法 member 进入 partial 结果而不是写出危险路径。

### Consequences

- EXTXYZ 周期转换复用成熟库。
- plain XYZ / EXTXYZ 的语义边界清晰。
- ZIP 解包的安全策略和解析结果状态有确定性测试覆盖。

## ADR-061：10 个 MVP Adapter 先完成库层覆盖，再接 Worker 编排

### Context

Milestone 0/1 已打通 `composition.ptable_heatmap`、`structure.structure_3d` 和 `structure.viewer_3d` 的 Tool Registry -> Adapter -> Artifact 本地闭环。Roadmap 要求 10 个 MVP 工具最终都能注册、校验并由 Worker 执行，但当前尚未实现 Job Queue、ToolCall 状态表、SSE 和生产 Artifact Service。

### Decision

先在 `packages/adapters` 完成全部 10 个 MVP Adapter 的库层覆盖，并全部注册到 `ADAPTER_CLASSES`：

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `structure.structure_3d`
- `structure.viewer_3d`
- `structure.coordination_hist`
- `ml.density_scatter`
- `ml.error_distribution`
- `ml.basic_metrics`
- `ml.outlier_table`

每个 Adapter 通过 `ToolExecutionRequest`、`ToolExecutionContext` 和本地 `LocalArtifactExporter` 生成标准 Artifact。该阶段只声明库层 smoke path 完成，不声明异步 Worker、数据库状态机或前端端到端完成。

### Consequences

- Tool Registry 中所有 MVP adapter class name 都能实际实例化，减少后续 Worker 接入风险。
- ML adapter 先共享 DataFrame target/prediction 校验和指标/outlier 计算，避免每个工具重复实现字段推断。
- 下一步 Job Queue / SSE / ToolCall 持久化可直接复用这些 Adapter，而不是再设计工具执行边界。
- V1/V2 manifest 中未实现 adapter 仍只校验为 registerable class name，待对应阶段实现。

## ADR-063：共享 Schema 必须同时暴露 Python 与 TypeScript 核心类型

### Context

Milestone 0/1 需要先打通 Python Adapter 和本地 Artifact 闭环，但后续 API、Worker、Agent Plan Validator 和前端工作台都会复用同一套类型。若 `packages/schemas` 只在 Python 侧完整、TypeScript 侧只覆盖 `RegisteredTool` 子集，前端和 API 合约容易再次分叉。

### Decision

`packages/schemas` 的阶段基线必须同时暴露 Python/Pydantic 与 TypeScript 核心类型，包括 `ArtifactType`、`DisplayTarget`、`ToolCategory`、`ToolDomain`、`ImplementationSource`、`MaterialObjectType`、`JobStatus`、`JobEventStatus`、`RegisteredTool`、`ToolExecutionRequest`、`ToolCall`、`Artifact`、`AnalysisPlan`、`AnalysisStep`、`DataProfile` 和 `VisualizationRecipe`。Python 侧补充 `JobEvent`，供后续 SSE / Agent Timeline 复用；JSON Schema 当前先覆盖 `RegisteredTool`，后续随 API/Plan Validator 扩展更多 schema 文件。

### Consequences

- 前端和 Worker 对 Tool Registry、Artifact、Plan、Recipe 的字段命名有同一入口。
- 共享 Schema 覆盖面由测试检查，避免后续只补一侧语言类型。
- 当前仍不声明完整 API 合约已完成；Job Queue、SSE、数据库持久化和前端集成进入下一阶段。

## ADR-064：库层 Tool Executor 先承担 Registry 校验与 Adapter 路由

### Context

`BaseToolAdapter` 已能执行单个 adapter 生命周期，但如果测试或后续 Worker 直接实例化 adapter，会绕过 Tool Registry lookup 和 manifest `paramsSchema` 校验，削弱“所有可执行能力必须经过 Tool Registry”的约束。完整 Job Queue、ToolCall 状态表、SSE 和数据库事务尚未进入当前实现阶段。

### Decision

先在 `packages/adapters` 提供库层 `execute_tool_request()` 作为受控执行入口。它接收 `ToolExecutionRequest` 和 `ToolExecutionContext`，按以下顺序执行：

```text
Tool Registry lookup
  -> input resolution / cache key
  -> paramsSchema validation
  -> optional in-memory cache lookup
  -> adapter class lookup from registry adapter name
  -> Adapter.execute()
  -> ToolExecutionResult
```

当前 cache 是可选内存映射，只作为后续 Redis / Artifact cache 的接口占位；当前结果不写数据库，不生成 JobEvent，不声明完整 Worker 编排完成。

### Consequences

- 后续 Worker 可以统一调用 `execute_tool_request()`，避免直接绕过 Registry 实例化 Adapter。
- manifest 中的 `paramsSchema` 开始有真实运行时约束。
- cache key 先稳定下来，后续可以接入 Redis / Artifact Service。
- ToolCall 状态更新、JobEvent `artifact.ready` 和持久化仍属于下一阶段。

## ADR-065：先用内存 Worker runtime 固化 JobEvent 与 ToolCall 语义

### Context

下一阶段需要 Celery、PostgreSQL、SSE、ToolCall 状态表和 Artifact ready 事件。如果直接进入完整基础设施，容易把队列、数据库事务和事件语义混在一起。当前已有 `execute_tool_request()` 可以安全执行单个 ToolCall，但尚未把结果投射为 JobEvent 和 ToolCall 状态。

### Decision

先在 `services/workers` 建立最小库层 runtime：

- `run_tool_call_job()` 调用 `execute_tool_request()`。
- `InMemoryJobStore` 记录开发环境下的 Job、ToolCall 和 JobEvent。
- 成功路径输出 `tool.started`、每个 Artifact 的 `artifact.ready`、`tool.completed`。
- 失败路径输出 `tool.failed`，并将 Job / ToolCall 标记为 failed。
- ToolCall params 在记录前对 secret-like keys 脱敏。

该 runtime 只作为语义基线和测试夹具，不替代后续 PostgreSQL repository、Celery task、SSE publisher 或 retry/cancel 状态机。

### Consequences

- 后续接数据库时可以按已有事件序列和 ToolCall 状态测试迁移。
- Artifact ready 事件 payload 的最小字段先稳定下来。
- Secret/BYOK 不进入 ToolCall 状态记录的规则已有测试覆盖。
- 仍需实现真实队列、持久化、SSE cursor、幂等重试和取消。

## ADR-066：MVP 工具参数必须使用白名单 paramsSchema

### Context

Agent 只能生成 JSON Analysis Plan，但如果已注册工具的 `paramsSchema` 允许任意 additional properties，合法 `tool_id` 仍可能携带未批准的上游 kwargs 或平台外参数，削弱 Tool Registry 作为执行白名单的边界。

### Decision

10 个 MVP 工具的 `paramsSchema` 必须使用 `additionalProperties=false`，只允许平台批准参数。当前已覆盖：

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `structure.structure_3d`
- `structure.viewer_3d`
- `structure.coordination_hist`
- `ml.density_scatter`
- `ml.error_distribution`
- `ml.basic_metrics`
- `ml.outlier_table`

V1/V2 工具在进入可执行阶段前也必须补齐白名单 paramsSchema；在此之前只能作为 manifest/register-only 能力存在。

### Consequences

- Agent Plan 即使引用合法工具，也不能传未注册参数。
- Adapter 参数映射与 manifest schema 需要同步维护。
- 上游 pymatviz API 差异必须记录到 `persistent/TOOL_REGISTRY_NOTES.md`，不能通过开放 kwargs 临时绕过。

## ADR-067：Milestone 1 先完成可验证 scaffold，不提前实现生产仓储

### Context

Roadmap 的 Milestone 1 要求完成项目骨架与基础设施：monorepo 结构、PostgreSQL / Redis / MinIO 配置、FastAPI 模块边界、Next.js 工作台 shell，以及基础 Auth / Project / Dataset 表。当前核心 Tool Registry / Adapter / Data Pipeline 库层已经先行完成，但 API、Web 和基础设施仍需要一个可测试的边界，供后续 Milestone 2 / 4 接入。

### Decision

Milestone 1 的完成标准定义为 scaffold 级可验证实现：

- `docker-compose.yml` 配置本地 PostgreSQL、Redis、MinIO。
- `apps/api/mdi_api` 提供 FastAPI app factory、配置加载、路由边界和 SQLAlchemy Core metadata。
- 基础表先定义为 metadata：`users`、`organizations`、`projects`、`project_members`、`datasets`、`files`。
- `apps/web` 提供 Next.js App Router 三栏式工作台 shell。
- 当前 API route 可返回 stub 或 Tool Registry 数据，但不声称已完成真实登录、项目仓储、上传服务、数据库迁移或 SSE。

### Consequences

- Phase 1 可以被 `python -m pytest -q`、`npm run typecheck` 和 `npm run build` 验证。
- 后续可以在不改边界的情况下接入 PostgreSQL repository、Celery worker、SSE publisher 和对象存储。
- 本阶段不把 stub route 误标为生产业务能力，避免与 Roadmap 后续 Milestone 混淆。
## ADR-09B-EVIDENCE: Official pymatviz examples evidence pack is demo evidence, not CI gate

### Context

Phase 9B needs teacher/demo evidence showing how the platform handles official pymatviz example data, while avoiding false claims for script-only, notebook-only, phonon, advanced widget, and richer visualization examples.

### Decision

Keep the official examples evidence pack outside the project repository and outside default CI. Treat it as presentation/demo evidence only. Direct-uploadable cases may be browser-verified through the Phase 9B workspace with Mock Planner. Script/notebook cases must be documented as partial unless they are converted into real uploadable platform inputs. Unsupported official capabilities must be marked `FUTURE_SCOPE`.

### Consequences

- The evidence pack can include screenshots, API responses, downloaded artifacts, and per-case summaries without bloating the repository.
- Default CI remains focused on unit, frontend, and service-backed integration tests and does not run browser evidence or real LLM calls.
- Current direct evidence proves persisted plan execution for `ml.basic_metrics`; richer official visualization coverage needs future Planner routing and adapter work.

## ADR-10B-1-COMPOSITION-ADAPTERS: Composition visualizations are deterministic adapters, not LLM-rendered plots

### Context

Phase 10B planning selected composition visualization as the next pymatviz-focused adapter batch because it is closer to material-informatics workflows than generic table plots while remaining lower risk than 3D structure, XRD, RDF, phonon, or Brillouin-zone rendering.

### Decision

Implement `composition.formula_statistics`, `composition.elements_hist`, `composition.ptable_heatmap`, `composition.chem_sys_treemap`, and `composition.chem_sys_sunburst` as deterministic Tool Registry + Adapter capabilities. Formula parsing, element counts, chemical systems, arity grouping, Plotly metadata, summaries, and recipes are generated inside adapters from validated table input. The LLM or Mock Planner may only select a structured tool call; it does not generate plot data directly and does not execute code.

### Consequences

- Composition artifacts are reproducible and auditable through JSON, `summary.md`, and `recipe.json`.
- Partial formula parsing failures become warnings unless no formula can be parsed.
- Browser/API evidence is a separate Phase 10B-2 task; Phase 10B-1 evidence is adapter-level only.
- QueueWorkerRuntime, AnalysisPlanRepository, `/planner/jobs`, and the Phase 9D live LLM gate remain unchanged.
