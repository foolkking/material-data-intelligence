# TOOL_REGISTRY_NOTES

## 2026-07-07 Phase 10C-1 Lightweight Structure Tool Notes

- Registered the Phase 10C-1 lightweight structure tool set:
  - `structure.summary`
  - `structure.lattice_summary`
  - `structure.spacegroup_summary`
  - `structure.composition_from_structure`
  - `structure.preview_metadata`
- All five tools use the `structure` domain, platform builtin implementation
  source, strict params schemas, bounded resource limits, deterministic artifact
  names, and JSON + `summary.md` + `recipe.json` outputs.
- Structure inputs are resolved only from platform-passed resources: pymatgen
  Structure objects, pymatgen Structure dict/JSON, normalized structure dicts,
  CIF text, POSCAR/CONTCAR text, or small collections of those resources.
  Adapters do not read arbitrary filesystem paths.
- `structure.spacegroup_summary` uses pymatgen/spglib when available. If the
  symmetry stack is unavailable or detection fails, the adapter reports typed
  dependency/detection errors or warnings; it must not fabricate `P1`,
  `Fm-3m`, or any other space group.
- Mock Planner structure routing runs before generic composition/table/viz
  routing. Explicit 3D viewer requests remain future-scope and are not treated
  as support for `structure.viewer_3d`.
- Phase 10C-1 evidence under `docs/phase10c/adapter_evidence/` is adapter-level
  only. Browser/API evidence is deferred to Phase 10C-2.
- No new tool may bypass AnalysisPlan validation, Tool Registry lookup, params
  schema validation, QueueWorkerRuntime, or Adapter execution.

## 2026-07-06 Phase 10C lightweight structure planning notes

- Phase 10C is planning-only and does not add, remove, or modify Tool Registry entries.
- Current evidence-grade adapter coverage includes table/viz first-batch tools and composition visualization tools. Structure tools remain a planning target until Phase 10C-1 implements and tests them.
- Recommended Phase 10C-1 tool scope: `structure.summary`, `structure.lattice_summary`, `structure.spacegroup_summary`, `structure.composition_from_structure`, and `structure.preview_metadata`.
- Planned structure tools must use the `structure` domain, strict params schemas, bounded resource limits, deterministic artifact names, and the existing registry-gated execution path.
- Planned outputs should be JSON + `summary.md` + `recipe.json`; 3D HTML viewers and physics plots are deferred.
- No future structure adapter may execute shell, arbitrary Python, network calls, uncontrolled filesystem reads/writes, or browser-side execution.
- Mapping-only README structure demos and future-scope phonon/Brillouin/XRD/RDF examples must not be marked as PASS until real inputs and evidence exist.

## 2026-07-06 Phase 10B composition visualization planning notes

- Phase 10B is planning-only and does not add, remove, or modify Tool Registry entries.
- Current registry already contains several composition and structure/physics tools beyond the Phase 10A evidence baseline. Phase 10B separates registered tools from evidence-grade tools.
- Phase 10A evidence-grade tools remain `table.distribution_summary`, `viz.scatter`, `viz.histogram`, `viz.correlation`, and `composition.summary`.
- Phase 10B-1 is recommended to harden/productize composition visualization tools through the same registry-gated path: AnalysisPlan JSON -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- Recommended Phase 10B-1 tool scope: `composition.ptable_heatmap`, `composition.elements_hist`, `composition.chem_sys_treemap`, `composition.chem_sys_sunburst`, and `composition.formula_statistics`.
- No future adapter may execute shell, arbitrary Python, network calls, uncontrolled filesystem reads/writes, or direct browser-side execution.
- Mapping-only README demos and extraction-required notebooks/scripts must not be marked as PASS until they have real inputs and evidence.

## 2026-07-06 Phase 10A-2 first-batch browser/API evidence notes

- The six Phase 10A-2 evidence scenarios all execute through the existing registry-gated path: AnalysisPlan JSON -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- `viz.scatter` and `viz.histogram` now export Plotly JSON artifacts with benchmark-facing metadata at the top level and the raw Plotly figure under `figure`. This keeps artifacts renderable while making evidence assertions deterministic.
- Mock Planner routing now checks composition-intent prompts before the generic histogram/distribution route, so Ward composition prompts select `composition.summary` instead of `viz.histogram`.
- No adapter executes shell, arbitrary Python, network calls, or uncontrolled filesystem writes.
- No real LLM is required for this evidence path, and default CI still does not call live providers.
- The official browser/API evidence is scoped to MatPES and Ward first-batch adapter scenarios. It must not be read as verification for extraction-required, mapping-only, or future-scope official examples.

## 2026-07-06 Phase 10A-1 first official table/viz adapter batch

- Added five registry-gated tools for the first two `DIRECT_VERIFIED` official pymatviz cases:
  `table.distribution_summary`, `viz.scatter`, `viz.histogram`, `viz.correlation`, and `composition.summary`.
- `table.distribution_summary` accepts a normalized DataFrame (`ml_table`) and emits `table_json`, `summary_md`, and `recipe_json` artifacts. It reports quantile distribution summaries, missing rates, categorical top values, recommended visualizations, and warnings.
- `viz.scatter` and `viz.histogram` use deterministic Plotly exports and emit named `plotly_json` / optional `plotly_html` artifacts plus summary and recipe artifacts.
- `viz.correlation` emits both `correlation_matrix.json` (`table_json`) and Plotly heatmap artifacts for numeric correlation analysis.
- `composition.summary` safely summarizes formula/composition columns only when such a column is present; it records parsed/failed formula counts and element/system summaries.
- Tool Registry manifests and params schemas are the enforcement boundary. The Mock Planner may route prompts to these tools, but PlanValidator still validates tool ID and params before persistence.
- Execution remains: AnalysisPlan JSON -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- No adapter executes shell, Python snippets, network calls, or arbitrary filesystem paths. No real LLM call is needed for these tools.

## 2026-07-05 Phase 9D live provider validation tightened params schema enforcement

- Phase 9D live verification showed that real provider output can select an allowed tool but still use invalid parameter aliases.
- PlanValidator now validates every step's `params` against the selected RegisteredTool `paramsSchema` before persistence, job creation, or enqueue.
- This is a Tool Registry boundary, not prompt trust: the planner prompt now lists allowed param names to guide models, but schema validation is the enforced rule.
- Valid live jobs still follow the registry-gated path: provider JSON AnalysisPlan -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- The Phase 9D evidence confirms a live Gemini plan executed through `ml.basic_metrics` and produced `metrics.json` / `summary.md` without secrets in JobEvent, Artifact, AnalysisPlan, or evidence files. The final gated full-chain verification passed with Gemini 3 Flash Preview.

## 2026-07-05 Phase 9D LLM config repair keeps execution registry-gated

- The Phase 9D repair changes provider configuration resolution, provider status reporting, UI status display, and gated live test coverage only.
- No Tool Registry manifest, adapter, PlanValidator rule, QueueWorkerRuntime behavior, or `/planner/jobs` persistence/enqueue semantics changed.
- Live provider output still must be JSON AnalysisPlan, then PlanValidator must approve it before persistence.
- Valid jobs still follow: provider JSON AnalysisPlan -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- Secret/API key values remain prohibited in prompts, plans, JobEvents, Artifacts, Reports, Recipes, UI browser storage, and test output.

## 2026-07-05 Phase 9C UI redesign does not change the Registry gate

- The Phase 9C docs update changes frontend information architecture only.
- The Phase 9C implementation also changes frontend information architecture only: top dataset/model dialogs, left data-context viewer, and main Agent/conversation/results tabs.
- No Tool Registry manifest, adapter implementation, tool scope, PlanValidator rule, QueueWorkerRuntime behavior, provider behavior, or `/planner/jobs` persistence/enqueue semantics changed.
- The new UI may show Agent process, conversation/Plan, and results/export as main workspace tabs, but it must not create a browser-side execution path.
- Valid jobs still follow: provider JSON AnalysisPlan -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> ToolCall/Artifact/Result provenance.
- Developer mode may reveal tool IDs, step IDs, plan IDs, plan hash, raw AnalysisPlan JSON, safe JobEvent payloads, and API responses, but Secret/API key values remain prohibited in UI storage, prompts, JobEvents, Artifacts, Reports, Recipes, and export packages.

## 2026-07-05 Phase 9B - table.numeric_summary added for semantic table summaries

- Added `table.numeric_summary` as an MVP platform builtin tool with `NumericSummaryAdapter`.
- The tool accepts a normalized DataFrame (`ml_table`) and emits `table_json`, `summary_md`, and `recipe_json` artifacts. The primary browser evidence artifact is `numeric_summary.json`.
- This tool is for descriptive table statistics. It prevents non-regression tables such as Ward metallic glasses from being forced through `ml.basic_metrics` with arbitrary target/prediction columns.
- Execution remains registry-gated: Mock Planner emits AnalysisPlan JSON, PlanValidator validates the registered tool and params schema, QueueWorkerRuntime loads the persisted plan by `job.plan_id`, and Adapter execution writes ToolCall/Artifact/Result provenance.
- MatPES remains a valid `ml.basic_metrics` case because the request is explicitly PBE vs r2SCAN numeric comparison.

## 2026-07-04 Phase 9B - MatPES blocker repair keeps execution registry-gated

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in this repair.
- The fix only changes Mock Planner parameter binding for `ml.basic_metrics`: it derives target/prediction params from the real DataProfile when available, then emits normal AnalysisPlan JSON.
- PlanValidator remains the enforced boundary before persistence; the plan is still persisted as an AnalysisPlan, bound by `jobs.plan_id`, loaded by QueueWorkerRuntime, and executed through Tool Registry lookup plus the `ml.basic_metrics` adapter.
- The repaired browser evidence proves `matpes_atomic_energies_csv` now executes one registry-approved `ml.basic_metrics` ToolCall with params `targetColumn=PBE` and `predictionColumn=r2SCAN`, creates one `metrics_json` artifact, and reaches `job.completed`.

## 2026-07-04 Phase 9B - durable worker object loading keeps execution registry-gated

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in this closure.
- `DurableObjectStoreResolver` reconstructs dataset objects only. It does not select tools, alter persisted AnalysisPlans, bypass PlanValidator, or execute code.
- The settings-driven `run_queued_job(job_id)` path still calls `QueueWorkerRuntime.handle_job(job_id)`, loads `job.plan_id`, reconstructs the persisted `AnalysisPlan`, and executes each step through Tool Registry lookup and Adapter execution.
- The new regression proves an out-of-process-style worker can load `ml_table` from persisted normalized exports and execute exactly one `ml.basic_metrics` ToolCall through the real adapter.
- Browser verification showed the UI provenance chain still reports `Loaded from persisted AnalysisPlan`, `Executed through Tool Registry + Adapter`, and `No deterministic fallback used`.

## 2026-07-04 Phase 9B - runtime data binding still preserves the Registry gate

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in this follow-up.
- Dataset object-store resolution is an input-binding step before tool execution. It supplies normalized objects such as `ml_table`, `structures`, and `formulas` to the worker; it does not select tools, mutate the persisted plan, or execute outside the registry.
- The local in-memory auto-drain path still calls `QueueWorkerRuntime.handle_job(job_id)`, which loads `job.plan_id`, reconstructs the persisted `AnalysisPlan`, emits `plan.loaded`, then executes each step through Tool Registry lookup and Adapter execution.
- The new inputRef validation rejects missing or unresolved uploaded-dataset references before AnalysisPlan persistence, Job creation, or enqueue. It strengthens the existing PlanValidator boundary for executable dataset binding.
- The uploaded CSV regression proves the persisted one-step `ml.basic_metrics` plan produces exactly one ToolCall through the adapter path, with `data.loaded` and `plan.loaded` provenance.
- Production Redis/service-backed execution remains the authoritative Phase 8B path; this follow-up only adds a local development/demo auto-run behavior and a resolver seam for dataset objects.

## 2026-07-04 Phase 9B - demo workspace still routes execution through Planner validation and Registry gate

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 9B.
- The new UI surfaces provider settings, dataset/profile selection, demo workflow, error explanations, artifacts, reports, and developer audit data; it does not create a frontend execution path.
- Planner jobs are still created only through `/planner/jobs`, and invalid plans still fail before AnalysisPlan persistence, Job creation, or queue enqueue.
- Provider connection tests may parse and validate a sample AnalysisPlan, but they do not execute tools, write ToolCalls, create Artifacts, or bypass PlanValidator.
- Demo dataset/profile support feeds the existing Phase2 runtime data/profile path. It does not allow the frontend to fabricate successful persisted plans or execution results.
- A valid planner job still follows the existing path: JSON AnalysisPlan -> PlanValidator -> persisted AnalysisPlan -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> Artifact/Result provenance.
- API keys are resolved server-side by `secretId` for provider tests and planner calls; they must never appear in ToolCall params, JobEvents, Artifacts, Recipes, Reports, or exported provenance.
- The Phase 9B follow-up only added browser CORS handling, safe runtime health probes, i18n cleanup, and invalid-plan response redaction. It did not change Tool Registry manifests, adapter routing, tool scope, or the persisted-plan execution gate.
- When PlanValidator rejects a credential-bearing plan, `/planner/jobs` now omits the rejected raw plan from the response, so credential-like params do not leak back to the browser or become pseudo-provenance.

## 2026-07-03 Phase 9A - true provider still stops at PlanValidator and Registry gate

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 9A.
- The OpenAI-compatible provider only returns structured planner JSON. It cannot execute Python, shell, filesystem, network, or adapter actions.
- Provider output must parse as JSON and construct an `AnalysisPlan`, then pass PlanValidator before `/planner/jobs` can persist a plan, create a job, or enqueue work.
- Unknown tools, V1/V2/non-MVP tools, duplicate steps, empty steps, and credential-like params remain rejected before persistence and before any Tool Registry/Adapter execution.
- A valid true-provider plan still follows the Phase 8B path: persisted `AnalysisPlan` -> `jobs.plan_id` -> QueueWorkerRuntime -> Tool Registry lookup -> Adapter -> Artifact/Result provenance.
- Provider failures and validation failures return safe errors and create no ToolCall, Artifact, JobEvent execution record, or queue message.

## 2026-07-03 Phase 8C-P1 - UX closure keeps Registry-gated execution unchanged

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 8C-P1.
- The new EventSource timeline only replays persisted JobEvents; it does not create an execution path and does not bypass Tool Registry validation.
- The new Report/Recipe Summary panel displays existing ToolCall/Artifact/Result provenance (`planId`/`planHash`) and does not synthesize execution records.
- The Dataset/Profile selector only improves data-context entry. It does not allow the frontend to create or mutate persisted AnalysisPlans.

## 2026-07-03 Phase 8C - frontend displays Registry-gated execution provenance

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 8C.
- The Planner workbench displays "Executed through Tool Registry + Adapter" as provenance text for persisted-plan jobs; it does not introduce a frontend execution path.
- Read-only planner APIs expose recorded ToolCall, Artifact, JobEvent, and Result provenance so the UI can show `planId`/`planHash` without bypassing registry validation.
- The frontend still creates work only through `/planner/jobs`; validation remains server-side and must pass before any plan is persisted or any job is created.
- The validation-failure UI explicitly states that no AnalysisPlan was saved, no Job was created, and nothing was enqueued.
- Deterministic fallback remains a dev/test fallback only for jobs without a persisted plan; Phase 8C does not reclassify fallback as a normal product path.

## 2026-07-03 Phase 8B - persisted plan execution still uses the Registry gate

- No Tool Registry manifest, adapter implementation, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 8B.
- Phase 8B changed where the validated plan is stored and loaded from: `/planner/jobs` persists the exact validated `AnalysisPlan`, and `QueueWorkerRuntime` loads it by `job.plan_id`.
- Execution is still controlled by the same path: persisted `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- The persisted 1-step test proves `toolId=ml.basic_metrics` and `stepId=llm_step_1` come from the persisted plan and produce exactly 1 ToolCall, not the deterministic 5-tool fallback.
- The Phase 8B targeted suite now includes a real adapter regression for persisted-plan execution, and CI run `28631817086` proved the same path against PostgreSQL + Redis + MinIO with 19 integration tests passed and 0 skipped.
- Unknown tools, V1/V2/non-MVP tools, duplicate steps, empty steps, and credential-like params are still rejected by PlanValidator before the plan can be saved or enqueued.
- Explicit worker fallback with caller-provided `plan` remains only for dev/test jobs that have no persisted `plan_id`; it is not the Phase 8B service-backed acceptance path.

## 2026-06-27 Phase 8A — validated plan executes through the same Registry gate

- No Tool Registry manifest, adapter, MVP/V1/V2 tool scope, or pymatviz mapping changed in Phase 8A.
- Phase 8A only changed the *source* of the plan executed by `create_job`: a validated LLM AnalysisPlan can now be the execution plan instead of the deterministic one. The execution path is unchanged — every step still goes through `run_tool_call_job` → Tool Registry lookup → paramsSchema validation → Adapter.
- The validated LLM plan still cannot reference unknown or non-MVP tools: `PlanValidator` (Phase 7) rejects them before any job is created. The Tool Registry remains the single execution gate.

## 2026-06-27 Phase 7 LLM Planner — Tool Registry as Execution Gate

- The LLM JSON Planner can ONLY select tools that exist in the Tool Registry. `PlanValidator` (in `packages/tool-registry/mdi_tool_registry/plan_validator.py`) rejects any `step.toolId` not present in `registry.tools` with `UNKNOWN_TOOL`.
- The LLM planner is restricted to **MVP-stage tools only**. `PlanValidator` rejects any tool whose `stage != "mvp"` with `NON_MVP_TOOL`. V1/V2 tools cannot be planned even if they exist in the registry.
- The planner prompt (`services/llm/mdi_llm/planner_prompt.py`) only lists MVP tools to the LLM, but the prompt is advisory — the Tool Registry + PlanValidator are the enforced execution gate, not the prompt.
- No new Tool Registry manifest, adapter, MVP/V1/V2 tool scope, or pymatviz API mapping changed in Phase 7. The planner is a new caller of the existing registry, not a registry change.
- The controlled execution path is unchanged and still mandatory:
  `LLM AnalysisPlan` -> `PlanValidator` -> (job creation) -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- `params` containing credential-like keys (api_key/token/password/secret/credential/authorization) are rejected at the validator level (`CREDENTIAL_IN_PARAMS`) before any tool runs.

## 2026-06-26 Phase 6 Service-backed Runtime Smoke Notes (Final)

- No Tool Registry manifest, adapter implementation, MVP tool scope, V1/V2 tool scope, or pymatviz API mapping changed in Phase 6.
- The service-backed product-loop integration test (`test_phase6_service_backed_product_loop`) was upgraded from fake executor to real Tool Registry + BasicMetricsAdapter execution via `execute_tool_request()`. A small in-memory DataFrame provides the regression input so no external fixture file is needed. All adapter validation (manifest paramsSchema check, Tool Registry lookup, adapter class instantiation) runs in the real path.
- The fake executor (`_fake_tool_executor`) remains available in the test file as a helper but is no longer used in the product-loop smoke test — it serves queue retry and idempotency tests where deterministic artifact shape matters more than adapter correctness.
- The product-loop smoke covers `ml.basic_metrics` through the same controlled execution path as the Phase 2/3/4/5 deterministic local tests:
  `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- Future phases that add real LLM or V1/V2 tools must extend the service-backed integration test to include those adapters through the same `execute_tool_request()` path.

## 2026-06-26 Phase 5 Runtime Infrastructure Notes

- No Tool Registry manifest, adapter implementation, MVP tool scope, V1/V2 tool scope, or pymatviz API mapping changed in Phase 5.
- The new `QueueWorkerRuntime` default execution path still constructs a `ToolExecutionRequest` and calls `execute_tool_request`, preserving:
  `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- Phase 5 queue tests use an injected fake executor only to validate queue retry/idempotency behavior without requiring real object inputs or rendering. This is a test seam, not a production bypass.
- Runtime infrastructure changes are limited to PostgreSQL configuration, queue dispatch/handler shape, JobEvent seq locking, and MinIO/S3 artifact object storage.
- No real LLM output, direct arbitrary Python/shell/filesystem/network execution by the Agent, V1/V2 tool execution, or direct pymatviz wrapper surface was introduced.

## 2026-06-26 Phase 4 Production Persistence Hardening Notes

- No Tool Registry manifest, adapter implementation, MVP tool scope, V1/V2 tool scope, or pymatviz API mapping changed in Phase 4.
- The controlled execution path remains:
  `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- Phase 4 only hardens persistence around the existing ToolCall and Artifact records: status validation, idempotent ToolCall writes, idempotent Artifact metadata writes, and transaction rollback behavior.
- The Phase 2 deterministic product loop still proves the same five registered MVP tools for the mixed CIF/POSCAR/CSV path; no real LLM output or direct executable action was introduced.
- Future queue workers must keep Tool Registry validation before writing ToolCall state and must not use the new repository idempotency hooks as a bypass around manifest validation.

## 2026-06-26 Phase 3 Persistence Foundation Notes

- No Tool Registry manifest, adapter class, MVP tool scope, V1/V2 tool scope, or pymatviz API mapping changed in Phase 3.
- Phase 3 repository and storage work preserves the controlled execution path:
  `AnalysisPlan` -> `ToolExecutionRequest` -> Tool Registry lookup -> paramsSchema validation -> Adapter -> Artifact.
- The Phase 2 deterministic product loop still selects the same five registered MVP tools for the mixed CIF/POSCAR/CSV path:
  `composition.ptable_heatmap`, `composition.chem_sys_treemap`, `structure.viewer_3d`, `ml.basic_metrics`, and `ml.outlier_table`.
- Phase 3 acceptance hardening did not change any manifest or adapter behavior; the product-loop regression still proves the same registry-approved MVP tool path.
- Artifact persistence now has local and S3/MinIO mapping metadata plus signed-url placeholder behavior, but registered visualization/analysis tools still produce artifacts through the existing adapter/exporter path.
- No V1/V2 tool execution, direct pymatviz exposure, real LLM tool execution, or bypass around Tool Registry validation was introduced.

## 2026-06-25 Phase 2 Acceptance Audit Notes

- Re-verified manifest loading from `tool_registry/pymatviz_manifest.yaml`, `tool_registry/matterviz_manifest.yaml`, and `tool_registry/platform_builtin_manifest.yaml`.
- The merged registry reports version `0.1.0` and 10 MVP tools.
- Phase 2 deterministic planning still uses only registered MVP tools:
  `composition.ptable_heatmap`, `composition.chem_sys_treemap`, `structure.viewer_3d`, `ml.basic_metrics`, and `ml.outlier_table`.
- Phase 2 generated `AnalysisPlan.expectedArtifacts` now follows the shared schema `{name, type, fromStepId}`.
- Phase 2 generated Recipe steps now include `toolVersion` and `inputBindings: Record<string, string>`.
- Shared Python/TypeScript schemas now expose named `ExpectedArtifact` and `VisualizationRecipeStep` types.
- No V1/V2 tool execution, direct pymatviz exposure, or LLM-directed executable action was introduced.

## 2026-06-25 Phase 2 Product Loop Notes

- The Phase 2 deterministic planner uses only registered MVP tools and does not introduce any V1/V2 tool execution.
- The default mixed CIF/POSCAR/CSV path selects five tools:
  `composition.ptable_heatmap`, `composition.chem_sys_treemap`, `structure.viewer_3d`, `ml.basic_metrics`, and `ml.outlier_table`.
- Every Phase 2 executable step is converted to `ToolExecutionRequest` and executed through:
  Tool Registry lookup -> artifact type validation -> paramsSchema validation -> adapter registry -> Adapter execution.
- No new pymatviz, MatterViz, Plotly, or platform-builtin API signature mismatch was found during this round.
- Job-level `analysis_plan_json`, `recipe_json`, `report_md`, and `report_html` artifacts are generated by platform system tool IDs and do not bypass Adapter execution for registered visualization/analysis tools.
- The local API can query ToolCall, JobEvent, Artifact, Recipe, and Report records from in-memory/local-file state. Durable PostgreSQL/MinIO state remains a later phase.

## 2026-06-25 Phase 1 Acceptance Notes

- All 10 MVP tools are now exercised in the Phase 1 product-flow acceptance test through Tool Registry + Adapter + Worker runtime.
- No new pymatviz API signature mismatch was found during this round.
- `preview_png` behavior changed from optional omission to deterministic artifact generation:
  when Plotly/Kaleido image export is unavailable, the adapter export helper writes a minimal valid PNG fallback.
- `structure.viewer_3d` keeps the existing graceful fallback contract:
  if `pymatviz.StructureWidget.to_html()` is unavailable or fails, the adapter writes sandbox-safe `matterviz_html` fallback content and records fallback provenance.
- The Phase 1 demo planner requests only registered artifact types from each tool manifest and uses the same `paramsSchema` validation path as normal execution.
- The runtime-generated Analysis Plan is deterministic and local; it is not a real LLM output and does not bypass the "Agent JSON Plan only" rule.

## External Capability Baseline

官方来源核对基线：

- pymatviz：materials informatics visualization toolkit；当前规划基线按 `0.18.x`、Python `>=3.11` 处理，正式实现前需要再次锁版本。
- pymatviz 输出以 Plotly Figure、HTML、图片、widget/export 为核心。
- MatterViz / anywidget 路线用于更接近浏览器原生的 3D 结构、轨迹和交互材料 UI。
- 平台不直接暴露 pymatviz 原始函数给 Agent；必须通过 Tool Registry + Adapter。
- `docs/14_PYMATVIZ_CAPABILITY_INVENTORY.md` 是 pymatviz 原始能力到平台 Tool ID 的能力清单。
- `docs/15_ADAPTER_IMPLEMENTATION_PLAN.md` 是 Adapter 实现顺序、接口和测试要求基线。

## Manifest-based Registry Baseline

正式实现时，Tool Registry 的首批工具来源为：

| Manifest | 作用 |
|---|---|
| `tool_registry/pymatviz_manifest.yaml` | pymatviz / pymatviz-composed capabilities such as `ptable_heatmap`, `structure_3d`, `coordination_hist`, and `density_scatter` |
| `tool_registry/matterviz_manifest.yaml` | MatterViz / widget 能力，例如 `StructureWidget` 和 `TrajectoryWidget` |
| `tool_registry/platform_builtin_manifest.yaml` | 平台内置分析和自定义 Plotly 能力，例如 `basic_metrics`、`outlier_table`、`error_distribution` |

每个 manifest tool entry 必须能映射到共享 Schema 中的 `RegisteredTool`，并保留：

- `tool_id`
- `implementation_source`
- `adapter`
- `display_target`
- `artifact_types`
- `stage`
- source package / source function / source class，如适用

`stage` 必须使用共享 Schema 允许的值：`mvp`、`v1`、`v2`。跨阶段探索能力不得写成组合枚举；例如 `structure.chem_env_sunburst` 默认登记为 `v2`，late V1 exploratory 只写入 `notes`。

## MVP Tool Source Split

| MVP Tool ID | Source |
|---|---|
| `composition.ptable_heatmap` | pymatviz `ptable_heatmap` |
| `composition.elements_hist` | pymatviz `elements_hist` |
| `composition.chem_sys_treemap` | pymatviz `chem_sys_treemap` |
| `structure.structure_3d` | pymatviz `structure_3d` |
| `structure.viewer_3d` | MatterViz / pymatviz `StructureWidget` |
| `structure.coordination_hist` | deterministic distance-cutoff static coordination histogram |
| `ml.density_scatter` | pymatviz `density_scatter` |
| `ml.error_distribution` | platform `plotly_custom` |
| `ml.basic_metrics` | platform builtin |
| `ml.outlier_table` | platform builtin |

## Initial Categories

### composition

- `composition.ptable_heatmap`
- `composition.elements_hist`
- `composition.chem_sys_treemap`
- `composition.cluster_2d`
- `composition.cluster_3d`

### structure

- `structure.viewer_3d`
- `structure.structure_3d`
- `structure.rdf`
- `structure.xrd`
- `structure.coordination_hist`
- `structure.spacegroup_bar`

### trajectory

- `trajectory.viewer`
- `trajectory.energy_curve`
- `trajectory.force_curve`

### phonon

- `phonon.band`
- `phonon.dos`
- `phonon.band_dos`

### ml

- `ml.parity_plot`
- `ml.density_scatter`
- `ml.error_distribution`
- `ml.basic_metrics`
- `ml.outlier_table`
- `ml.uncertainty_calibration`
- `ml.confusion_matrix`
- `ml.error_by_element`
- `ml.error_by_chem_sys`

## Accepted Data Forms

| 数据类别 | 典型 Python 形式 | 平台标准化目标 |
|---|---|---|
| 化学式 / 组成 | string formula、`pymatgen.Composition` | `Composition[]`、formula column |
| 晶体结构 | `pymatgen.Structure`、`IStructure`、`ASE Atoms`、`PhonopyAtoms` | `Structure[]` + structure metadata |
| 结构文件 | CIF、POSCAR、CONTCAR、JSON limited | parsed structure collection |
| 表格数据 | `pandas.DataFrame` | typed dataframe + inferred field roles |
| 数值数组 | numpy/list/Series | metric arrays or chart series |
| 声子数据 | pymatgen / phonopy band、DOS objects | phonon band/DOS profile |
| 轨迹数据 | ASE traj、EXTXYZ、pymatgen trajectory JSON、XDATCAR | trajectory frames + per-frame properties |
| 模型结果 | `y_true`、`y_pred`、`y_std`、labels、probabilities | ML evaluation dataset |

## Data to Visualization Mapping

| 输入 | Tool IDs | 产物 |
|---|---|---|
| 化学式列表 | `composition.ptable_heatmap`、`composition.elements_hist`、`composition.chem_sys_treemap` | 周期表热力图、元素直方图、化学体系 treemap |
| 化学式 + 性质 | `composition.cluster_2d`、`composition.cluster_3d` | 组成嵌入 2D/3D 聚类图 |
| Structure collection | `structure.structure_3d`、`structure.viewer_3d`、`structure.spacegroup_bar` | Plotly 3D、MatterViz 3D、空间群分布 |
| Structure + local geometry | `structure.rdf`、`structure.xrd`、`structure.coordination_hist` | RDF、XRD、配位数分布 |
| Structure + force/magmom | `structure.structure_3d`、`trajectory.viewer` | 带向量箭头结构图、轨迹/优化过程 |
| phonopy / pymatgen phonon | `phonon.band`、`phonon.dos`、`phonon.band_dos` | 声子能带、声子 DOS、组合图 |
| `y_true` / `y_pred` | MVP：`ml.density_scatter`、`ml.error_distribution`、`ml.basic_metrics`、`ml.outlier_table`；V1：`ml.parity_plot` | density scatter、误差分布、指标、离群表 |
| `y_true` / `y_pred` / `y_std` | `ml.uncertainty_calibration` | 不确定性校准、error decay |
| 分类标签 | `ml.confusion_matrix` | 混淆矩阵、分类指标图 |

## MVP Tool Set

MVP 优先封装以下工具，保证“结构数据 + 预测结果表格”两条核心路径闭环：

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

V1/V2 再扩展：

- `structure.rdf`
- `structure.xrd`
- `structure.spacegroup_bar`
- `composition.cluster_2d`
- `composition.cluster_3d`
- `ml.parity_plot`
- `phonon.band`
- `phonon.dos`
- `trajectory.viewer`
- `ml.uncertainty_calibration`
- `ml.error_by_element`
- `ml.error_by_chem_sys`

## 3D Rendering Routes

| 路线 | 适用场景 | 产物 |
|---|---|---|
| Plotly `structure_3d` | 快速结构图、图表卡片、HTML 交互图 | MVP：Plotly JSON、HTML、PNG preview；V1：SVG/PDF 论文图 |
| MatterViz `StructureWidget` | 浏览器结构查看、交互检查、材料 Viewer | viewer HTML、metadata、optional snapshot |
| MatterViz `TrajectoryWidget` | MD / relaxation 轨迹、帧属性曲线、force vectors | V1：trajectory HTML、optional snapshot、per-frame metadata |

所有 3D 工具必须支持结构大小分级策略：小结构完整显示，中结构默认减少 bonds，大结构启用 LOD / 抽样 / 手动展开，trajectory 默认抽帧。

## Tool Schema Draft

Phase 6 已将 Tool Schema 固化到 `docs/06_TOOL_REGISTRY_AND_ADAPTER.md`，共享枚举和跨模块类型收敛到 `docs/13_SHARED_SCHEMA_SPEC.md`。后续实现以这两个文档为准。

```ts
type RegisteredTool = {
  toolId: string;
  name: string;
  category: ToolCategory;
  domain: ToolDomain;
  implementationSource: ImplementationSource;
  description: string;
  version: string;
  adapter: string;
  inputSchema: ToolInputSchema; // uses inputOptions OR semantics
  paramsSchema: Record<string, unknown>;
  artifactTypes: ArtifactType[];
  costLevel: "low" | "medium" | "high";
  timeoutSec: number;
  cachePolicy: "reuse" | "refresh" | "no_cache";
};
```

## Artifact Requirements

每个工具输出不只保存最终图，还要保存复现与审计所需材料：

| Artifact | 说明 |
|---|---|
| `figure.json` | Plotly Figure JSON 或等价结构化图表描述 |
| `figure.html` | 可交互 HTML |
| `preview.png` | 卡片预览图 |
| `figure.svg` / `figure.pdf` | 论文/报告导出，V1 |
| `viewer.html` | MatterViz / 3D viewer HTML |
| `metadata.json` | MatterViz viewer 元数据 |
| `structure.json` | 标准化结构或结构引用 |
| `metrics.json` | MAE、RMSE、R2、error stats 等结构化指标 |
| `table.json` | outlier table、failed files、quality issues 等小表 |
| `table.csv` | 用户下载表格 |
| `quality_issues.json` | 解析失败、字段问题、结构质量问题 |
| `summary.md` | 图表解释、数据来源、关键参数 |
| `recipe.json` | 复现该工具调用的输入引用、参数、版本 |

## Agent Display Contract

前端展示的是结构化可审计过程，不展示 LLM 原始隐藏思维链：

```text
Data Detection -> Data Quality -> Plan Generated -> Tool Started -> Artifact Ready -> Result Explanation
```

每个 ToolCall 至少展示：

- 为什么选择该工具。
- 使用哪些输入数据。
- 关键参数是什么。
- 输出了哪些 Artifact。
- 是否命中缓存。
- 是否有 Warning / Error。

## Open Tool Design Issues

- V1 是否将 pymatviz 函数签名半自动转换为 Tool Schema？
- V1 phonon、trajectory 工具的首批 Tool ID 如何排序？
- V2 VASP、LAMMPS 工具的首批 Tool ID 如何排序？
- Expert 模式是否允许用户编辑 Recipe 和受限 Python 代码片段？

## Implementation Notes 2026-06-25

### Verified Runtime Versions

本轮以当前可安装运行版本核对前三个 Adapter：

| Package | Version |
|---|---|
| `pymatviz` | `0.18.0` |
| `pymatgen` | `2026.5.4` |
| `ase` | `3.29.0` |
| `plotly` | `6.8.0` |

为兼容当前全局环境的 NumPy 2.x，还升级了 `xarray`、`pyarrow`、`numexpr`、`bottleneck`、`shapely` 和 `scikit-image`。后续建议改为项目专用 virtualenv/lockfile。

### API Signature Mapping

| Tool ID | Verified source | Observed signature note | Adapter mapping |
|---|---|---|---|
| `composition.ptable_heatmap` | `pymatviz.ptable_heatmap` | `values` 为首参，真实参数为 `count_mode`、`colorscale`、`heat_mode` 等 | 平台参数 `colorScale` -> `colorscale`；`countMode` 和 `normalize` 先由 adapter 侧聚合/归一化元素值，再调用 `ptable_heatmap(values)` |
| `composition.elements_hist` | `pymatviz.elements_hist` | 首参为 `formulas`；`fig_kwargs` 会直接传给 `go.Figure(**fig_kwargs)`，不能用 `{"title": ...}` | 平台参数 `countMode` -> `count_mode`、`keepTop` -> `keep_top`、`logY` -> `log_y`、`showValues` -> `show_values`；标题通过 `fig.update_layout(title_text=...)` 设置 |
| `composition.chem_sys_treemap` | `pymatviz.chem_sys_treemap` | 接受 formula、Composition、Structure 序列；参数为 `show_counts`、`max_cells` 等 | 平台参数 `showCounts` -> `show_counts`、`maxCells` -> `max_cells`；Adapter 负责从 Structure 派生 composition 输入 |
| `structure.structure_3d` | `pymatviz.structure_3d` | 支持 `Structure`、`dict[str, Structure]`、`Sequence[Structure]`；参数为 `show_cell`、`show_bonds` 等 | 平台参数 `showCell` -> `show_cell`；`showBonds: "auto"` 在 MVP 映射为 `False`；先校验周期 lattice 和 atom limit |
| `structure.coordination_hist` | deterministic distance-cutoff coordination count | Supports platform-passed periodic Structure objects, Structure dicts, CIF/POSCAR text, and bounded structure sequences through the Phase 10C parser | Emits `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, and `recipe.json`; params are `neighbor_policy`, `cutoff_angstrom`, `max_sites`, `max_neighbors_per_site`, `include_site_details`, `group_by_element`, `include_pair_counts`, and `plot_kind`; no HTML, no artifact JS, no advanced local-environment classification |
| `structure.viewer_3d` | `pymatviz.StructureWidget` | 构造函数为 `(structure=None, **kwargs)`，实例提供 `to_html()` | 优先输出 `StructureWidget.to_html()`；如 widget 渲染失败，输出 sandbox-safe fallback HTML 并在 provenance 中标记 `mattervizFallback=true` |
| `ml.density_scatter` | `pymatviz.density_scatter` | 参数为 `x`、`y` 和可选 `df`；`n_bins=False` 可用于小型 smoke test 禁用分箱 | 平台参数 `targetColumn` / `predictionColumn` 解析到 DataFrame 列名，`nBins` -> `n_bins`、`identityLine` -> `identity_line`、`bestFitLine` -> `best_fit_line` |
| `ml.error_distribution` | `plotly.express.histogram` | 平台自定义 Plotly 工具，无 pymatviz 原生函数依赖 | Adapter 计算 `prediction - target` 的 error 列，输出 histogram、metrics_json 和 top outlier table_json |
| `ml.basic_metrics` | platform builtin | 平台内置计算 MAE、RMSE、R2、meanError、maxAbsError | Adapter 使用 DataFrame target/prediction 列，输出 canonical `metrics_json` |
| `ml.outlier_table` | platform builtin | 平台内置按 `abs_error` 降序生成 top-k 表 | Adapter 输出 `table_json` 和 `table_csv`，不依赖 Plotly |

### Optional / Fallback Notes

- `preview_png` 仍按 MVP optional 处理；当前 exporter 仅在请求 `preview_png` 且 Plotly/Kaleido 可用时生成，不作为测试阻塞项。
- `structure.viewer_3d` 已输出 `matterviz_html`、`structure_json`、`summary_md`、`recipe_json`；snapshot 仍推迟到 V1 或后续 render-worker。
- 10 个 MVP manifest adapter 现在均已注册到 `ADAPTER_CLASSES` 并有 smoke tests；V1/V2 adapter 仍通过 registerable class name 校验，待对应阶段实现。

### Data Pipeline Contract Notes

- `packages/material-parsers` 现在可产生 `MaterialObjectType.Structure` 和 `MaterialObjectType.DataFrame` normalized object draft，字段与 Tool Registry inputOptions 对齐。
- `structure.structure_3d` 仍要求 periodic `Structure`；plain XYZ 当前会解析为非周期 `Atoms` normalized object，并生成 `NON_PERIODIC_ATOMS` quality warning，不会被误路由到周期结构工具。
- `.extxyz` 文件现在按扩展名直接识别为 `extxyz`，由 ASE 解析并在具备 lattice 时转换成周期 `Structure`。
- ZIP 容器解析已具备安全 member path 过滤：`../`、绝对路径和过深路径会被拒绝，保留安全 member 继续解析并标记 partial。
- `DataFrame` parser 会推断 `formula`、`target`、`prediction`、`uncertainty`、`structure_id` 字段角色，为后续 ML MVP tools 的 Tool Registry 校验做准备。

### Shared Schema Verification Notes

- Python/Pydantic 入口 `mdi_schemas` 已导出本阶段要求的核心类型；本轮补充了 `JobEvent` 以对齐 SSE / Timeline 设计。
- TypeScript 入口 `packages/schemas/src/index.ts` 已补齐 `JobStatus`、`JobEventStatus`、`ToolExecutionRequest`、`ToolCall`、`Artifact`、`AnalysisPlan`、`AnalysisStep`、`DataProfile`、`VisualizationRecipe` 等核心类型。
- 新增 `tests/test_shared_schemas.py`，防止 Python 与 TypeScript schema 入口再次出现核心类型覆盖差异。
- 当前未发现新的 pymatviz API 签名差异；`preview_png` 仍因 Kaleido/Chromium 作为 optional artifact 处理。

### Tool Executor Notes

- 新增 `mdi_adapters.execute_tool_request()` 作为库层受控执行入口，后续 Worker 不应直接实例化 adapter 跳过 Registry。
- 当前执行入口会校验 tool 是否存在于 manifest、请求 artifact type 是否属于 `RegisteredTool.artifactTypes`、`params` 是否符合 `paramsSchema`，再通过 adapter registry 创建 Adapter。
- cache key 由 `toolId`、tool version、adapter name、input hashes、params 和 artifact types 计算；当前仅支持可选 in-memory cache，占位后续 Redis / Artifact cache。
- 当前尚未接入 ToolCall 数据库状态更新和 JobEvent `artifact.ready`；这属于 Job Queue / SSE 阶段。

### Worker Runtime Notes

- 新增 `mdi_workers.run_tool_call_job()`，将 `execute_tool_request()` 的结果投射为 ToolCall 状态和 JobEvent 事件序列。
- 成功路径事件顺序为 `tool.started` -> `artifact.ready`* -> `tool.completed`，每个 Artifact 单独产生 `artifact.ready`。
- 失败路径事件顺序为 `tool.started` -> `tool.failed`，Job 和 ToolCall 均标记为 failed。
- 当前 `InMemoryJobStore` 仅用于开发和测试；生产仍需 PostgreSQL 状态源、SSE publisher、Worker retry/cancel 和幂等写入。
- ToolCall params 在写入状态前会脱敏 secret-like keys，避免 BYOK/API key 进入状态记录。

### MVP Params Schema Notes

- 本轮恢复核验后，将全部 10 个 MVP 工具的 `paramsSchema` 收紧为白名单，统一使用 `additionalProperties=false`。
- 受控执行入口 `execute_tool_request()` 现在可对所有 MVP 工具拒绝未注册参数，而不只覆盖前三个 Adapter。
- 当前已显式声明的平台批准参数包括：
  - composition：`countMode`、`colorScale`、`normalize`、`keepTop`、`logY`、`showValues`、`showCounts`、`maxCells`、`title`
  - structure: `showCell`, `showBonds`, `selectedStructureIds`, `selectedStructureId`, `cameraPreset`, `maxStructures`, `neighbor_policy`, `cutoff_angstrom`, `max_sites`, `max_neighbors_per_site`, `include_site_details`, `group_by_element`, `include_pair_counts`, `plot_kind`
  - ml：`targetColumn`、`predictionColumn`、`nBins`、`density`、`xLabel`、`yLabel`、`identityLine`、`bestFitLine`、`stats`、`topK`、`title`
- 新增测试确保 MVP 工具未知参数会触发 JSON Schema `Additional properties are not allowed`。
- 未发现新的 pymatviz API 与 manifest 差异；`preview_png` 继续作为 optional/fallback artifact 处理。

### Phase 1 API Boundary Notes

- `apps/api/mdi_api` 已提供 FastAPI app factory，并通过 `/tools` 与 `/tools/mvp` 暴露 Tool Registry 的只读查询边界。
- 工具查询 route 只返回 manifest-normalized registry view，不执行 adapter，不绕过 `execute_tool_request()`。
- 后续执行类 API 必须继续走 Tool Registry lookup、paramsSchema 校验和 adapter registry，不允许 API route 直接实例化 pymatviz 函数。
## 2026-07-04 Official Example Evidence Notes

- Direct official browser evidence currently validates the Tool Registry + Adapter path for `ml.basic_metrics` only.
- MatPES evidence selected `PBE` and `r2SCAN` from the DataProfile and produced a `metrics_json` artifact.
- Ward metallic glasses evidence now routes to `table.numeric_summary`; `D_max` and `dTx` are summarized as independent numeric properties instead of being treated as target/prediction metrics columns.
- Official richer tools such as `plotly_custom.histogram`, `composition.ptable_heatmap`, `composition.elements_hist`, classification curves, phonon tools, Brillouin zone, and MatterViz widgets were not downgraded into current PASS. They are preserved as future expected tools in the evidence pack.
- No evidence path bypassed Tool Registry or Adapter execution.

## 2026-07-06 Phase 10B-1 Composition Visualization Tool Notes

- Registered or upgraded the executable composition visualization set:
  - `composition.formula_statistics`
  - `composition.elements_hist`
  - `composition.ptable_heatmap`
  - `composition.chem_sys_treemap`
  - `composition.chem_sys_sunburst`
- These tools use DataFrame input with deterministic formula column resolution. Explicit `formulaColumn` takes priority; otherwise the resolver checks `formula`, `composition`, `reduced_formula`, `pretty_formula`, `material_formula`, and `chemical_formula`.
- `paramsSchema` remains a whitelist. Unknown params are rejected through Tool Registry validation before adapter execution.
- Required artifacts are deterministic JSON plus `summary.md` and `recipe.json`; Plotly HTML is produced when supported.
- Adapter execution does not access network, execute shell, read arbitrary paths, or use a real LLM.
- Mock Planner routing now checks explicit composition keywords before generic histogram/correlation/table routing to avoid misrouting composition prompts.

## 2026-07-06 Phase 10B-2 Composition Browser/API Evidence Notes

- Browser/API evidence confirms all five composition visualization tools execute through persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- Verified tools:
  - `composition.formula_statistics`
  - `composition.elements_hist`
  - `composition.ptable_heatmap`
  - `composition.chem_sys_treemap`
  - `composition.chem_sys_sunburst`
- Evidence artifacts live under `docs/phase10b/browser_api_evidence/` and include redacted API captures, screenshots, copied artifact files, manifests, and platform summaries.
- `composition.ptable_heatmap` now emits `ptable_heatmap.json` to match the registered artifact contract and evidence expectations.
- No tool execution path was allowed to bypass Tool Registry or Adapter execution.
- No new adapter was added in Phase 10B-2.

## 2026-07-07 Phase 10C-2 Structure Browser/API Evidence Notes

- Browser/API evidence confirms all five lightweight structure tools execute through persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- Verified tools:
  - `structure.summary`
  - `structure.lattice_summary`
  - `structure.spacegroup_summary`
  - `structure.composition_from_structure`
  - `structure.preview_metadata`
- Evidence artifacts live under `docs/phase10c/browser_api_evidence/` and include redacted API captures, screenshots, copied artifact files, manifests, and platform summaries.
- No tool execution path was allowed to bypass Tool Registry or Adapter execution.
- No new adapter was added in Phase 10C-2.
- Phase 10C-2 does not claim support for `structure.viewer_3d`, XRD, RDF, coordination histogram, phonon, or Brillouin zone tools.

## 2026-07-07 Phase 10D Advanced Structure Planning Notes

- Phase 10D is planning-only and does not register new tools.
- Future advanced structure tools must still enter through Tool Registry validation, whitelist params schemas, resource limits, and Adapter execution.
- Recommended Phase 10D-1 executable candidates are:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
  - optional schema-only `structure.viewer_3d_contract`
- Full `structure.viewer_3d`, `structure.brillouin_zone_3d`, `structure.xrd`, `structure.rdf`, `phonon.bands`, `phonon.dos`, and `phonon.band_dos` remain unregistered future-scope tools until their schemas, dependencies, and evidence plans are approved.
- Viewer artifacts must be static and deterministic. Artifact-provided JavaScript execution, external URL loading, arbitrary local file reads, notebook execution, and script execution remain forbidden.

## 2026-07-07 Phase 10D-1 Viewer Scene Metadata Tool Notes

- Registered executable tools:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- Both tools use domain `structure`, strict params schemas, Tool Registry validation, and Adapter execution.
- `structure.viewer_scene_metadata` emits `viewer_scene.json`, `summary.md`, and `recipe.json`.
- `structure.viewer_export_package` emits `viewer_scene.json`, `viewer_assets_manifest.json`, `summary.md`, and `recipe.json`.
- Artifacts are static JSON/Markdown only. They do not include renderer bundles, artifact-supplied JavaScript, external URLs, or WebGL code.
- Mock Planner routing for full interactive viewer, XRD, RDF, coordination, Brillouin-zone, and phonon prompts remains deferred and does not route to Phase 10D-1 tools.

## 2026-07-08 Phase 10D-2 Viewer Scene Evidence Notes

- No new Tool Registry tools were added in Phase 10D-2.
- Browser/API evidence confirms the existing `structure.viewer_scene_metadata` and `structure.viewer_export_package` tools execute through Mock Planner, PlanValidator, persisted AnalysisPlan, QueueWorkerRuntime, Tool Registry validation, and adapter execution.
- Evidence artifacts live under `docs/phase10d/browser_api_evidence/` and include redacted API captures, browser-rendered static preview screenshots, copied artifact files, manifests, and platform summaries.
- Verified artifacts:
  - `viewer_scene.json`
  - `viewer_assets_manifest.json`
  - `summary.md`
  - `recipe.json`
- The evidence confirms static metadata/export package behavior only. It does not register or claim `structure.viewer_3d`, `structure.brillouin_zone_3d`, `structure.xrd`, `structure.rdf`, `structure.coordination_hist`, `phonon.bands`, or `phonon.dos`.
- No tool execution path was allowed to bypass Tool Registry or Adapter execution.

## 2026-07-08 Phase 10D-3 Static Preview Notes

- No new Tool Registry tools were added in Phase 10D-3.
- Existing registered tools remain:
  - `structure.viewer_scene_metadata`
  - `structure.viewer_export_package`
- Frontend artifact preview now recognizes the static artifact contracts emitted by those tools:
  - `viewer_scene.json`
  - `viewer_assets_manifest.json`
  - `summary.md`
  - `recipe.json`
- Preview hardening does not change adapter execution, Tool Registry validation, PlanValidator, QueueWorkerRuntime, or `/planner/jobs`.
- Static previews must not be interpreted as support for `structure.viewer_3d`, WebGL rendering, Brillouin-zone 3D, XRD, RDF, coordination histogram, phonon, notebook extraction, or script execution.

## 2026-07-08 Phase 10E Static Physics Planning Notes

- No new Tool Registry tools were added in Phase 10E.
- Planned future tool ids:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- Planned domain for all three is `structure`.
- Planned outputs follow existing artifact boundaries: deterministic numeric JSON, optional static Plotly-compatible chart JSON/HTML, `summary.md`, and `recipe.json`.
- Recommended first implementation is `structure.coordination_hist`; it must require periodic structures and a strict params schema.
- `structure.xrd` and `structure.rdf` must not be registered until numeric tolerance and fixture policies are pinned.
- Full `structure.viewer_3d`, Brillouin-zone 3D, phonon tools, notebook/script execution, external API workflows, and experimental fitting remain outside Tool Registry scope.

## 2026-07-08 Phase 10E-1 Coordination Histogram Tool Notes

- `structure.coordination_hist` is now implemented and executable through Tool Registry + Adapter.
- The adapter uses a deterministic `distance_cutoff` neighbor policy and does not call `pymatviz.coordination_hist` directly.
- Registered artifacts are:
  - `coordination_hist.json` as `table_json`
  - `coordination_hist_plot.json` as `plotly_json`
  - `summary.md` as `summary_md`
  - `recipe.json` as `recipe_json`
- The strict params schema allows only `neighbor_policy`, `cutoff_angstrom`, `max_sites`, `max_neighbors_per_site`, `include_site_details`, `group_by_element`, `include_pair_counts`, and `plot_kind`.
- The tool does not emit HTML, executable JavaScript, external URLs, WebGL renderer assets, or full 3D viewer artifacts.
- XRD, RDF, full viewer, WebGL, Brillouin-zone, phonon, Voronoi, CrystalNN, bond-valence, notebook/script, and external API workflows remain out of scope.
