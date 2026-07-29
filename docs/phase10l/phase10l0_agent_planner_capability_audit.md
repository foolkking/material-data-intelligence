# Phase 10L-0 Agent / Planner Capability Audit

## Audit Result

The current product is best classified as a
**PROFILE_AWARE_SINGLE_TOOL_PLANNER with one narrow sequential-independent
two-tool composition**. On the five-level assessment used for this gate it is
**Level 3: data/profile-aware tool selection**, but Level 3 coverage is uneven
across domains. It is not a capability-aware multi-tool planner.

Production Planner behavior changes in Phase 10L-0: **NONE**.

## Baseline

| Item | Value |
|---|---|
| Phase 10K | Complete, `READY_WITH_EXPLICIT_LIMITS` |
| Phase 10K-5 implementation | `e4639a1168f4bac7f4c786c48657559038bd7230` |
| Phase 10K-5 completion record | `81d44467c9b0d9e8bef3d4dec38d6a85e3d2aebe` |
| Phase 10K archive | `17de1f91cef6e94a5a1f4ae684fb3e1b756f0906`, CI `30382914410` |
| Audit branch | `master` |
| Initial audit HEAD/origin | `17de1f91cef6e94a5a1f4ae684fb3e1b756f0906` |

## Mock Planner Decision Inputs

The provider contains 34 `_should_generate_*` predicates, one separate
materials-ML selector, 19 named Mock plan builders, and 56 prompt-check sites.
These counts describe the audited baseline, not a target architecture.

| Signal | Used | How |
|---|---:|---|
| Raw prompt | Yes | Lower-cased phrase/substring rules and limited regex extraction |
| Keywords | Yes | Primary routing mechanism and fixed-priority `elif` ordering |
| Resource kind | Partial | Structure/trajectory/phonon/volumetric predicates inspect Profile summaries, objects, or dataset type |
| DataProfile | Yes | Passed as a typed object to every Mock generation call |
| Profile 2.0 semantic roles | Partial | Used by product-level ML, Composition Space, and selected column helpers |
| Profile readiness | Partial | Used for Composition Space and ambiguous ML handling, not universally |
| Tool Registry | Partial | Checks whether fixed tool IDs exist; it does not rank candidates from capability metadata |
| Explicit tool IDs | Partial | Dedicated legacy/export phrases exist; no generic safe tool-ID command parser |
| Previous artifacts | No | No prior-plan or prior-artifact context |

Mock Planner classification: **PARTIAL_PROFILE_AWARE**. New Phase 10K
product-level tools use exact Profile semantics, while many older routes remain
keyword plus hard-coded defaults. Unmatched requests fall back to
`ml.basic_metrics`, even when a non-table resource is present.

## DataProfile Consumption

| Profile information | Mock Planner | LLM Planner | PlanValidator |
|---|---|---|---|
| Dataset/resource kind | Partial direct checks | Table/structure only in shallow text | No |
| Formula/composition | Column selection and K4 eligibility | Input-ref hint only | No |
| Material properties | Partial column/color selection | Column names only | No |
| Structure presence | Yes | Count and elements | No |
| Trajectory | Yes | No | No |
| Phonon | Yes | No | No |
| Volumetric | Yes | No | No |
| Regression task | Complete semantic groups for K3 | No semantic groups | No |
| Uncertainty | Complete regression groups with uncertainty | No | No |
| Classification | Complete classification groups | No | No |
| Analysis readiness | Partial | No | No |

The API additionally checks normalized-object refs against the local object
store when one exists. That is an execution-input check, not semantic Profile
eligibility validation.

## LLM Planner Context

| Context | Present | Detail |
|---|---:|---|
| User prompt | Yes | Raw prompt |
| Dataset/profile IDs | Yes | String IDs |
| Full Profile 2.0 | No | Not serialized |
| Table columns | Yes | Names only |
| Structure summary | Partial | Count and first 20 elements |
| Quality issues | Partial | Count only |
| Tool IDs/descriptions | Yes | All 41 MVP tools |
| Allowed parameter names | Yes | Names, not full constraints |
| Artifact types | Yes | Enum values per tool |
| Input schemas/resource requirements | No | Not in prompt |
| Resource limits/cost/timeouts | No | Not in prompt |
| Semantic eligibility/planner hints | No | Not represented |
| Previous errors/plan/history | No | No repair or multi-turn context |
| Max tools/plan complexity rule | No | No plan-level cap |

The provider asks for JSON object mode. Fenced JSON is parsed permissively and
then PlanValidator is mandatory. There is no invalid-plan re-prompt,
scientific repair loop, or Mock fallback. A response-format HTTP 400 may cause
one transport compatibility retry without `response_format`; this is not plan
repair. Default timeout, temperature, and output token values exist, but API
request models do not impose upper bounds on prompt length, max tokens, or
temperature.

`REAL_LLM_CALLS = 0` for this audit.

## Tool Registry Planner Readiness

Baseline inventory: **53 tools**, of which **41 are MVP**, across 8 domains:
composition 11, dataset 2, ML 11, phonon 4, structure 19, table 2,
trajectory 1, and visualization 3.

| Metadata | State |
|---|---|
| Tool identity/domain/category/description | Present |
| Input object options | Present |
| Params JSON Schema | Present |
| Output artifacts/display target | Present |
| Cost/timeouts/cache/permissions/resource caps | Present |
| Scientific semantic prerequisites | Mostly absent as machine-readable planner requirements |
| Profile readiness mapping | Absent |
| Planner ranking/hints/collision groups | Absent |

Classification: **PARTIAL_PLANNER_CAPABILITY_REGISTRY**. It is a strong
execution registry and a useful source of planner context, but cannot by itself
answer whether a specific Profile is eligible for a tool. Product-level K2-K4
tools improve granularity, while low-level table/visualization tools and legacy
viewer identities still create overlapping choices.

## PlanValidator

Classification: **SCHEMA_AND_REGISTRY_VALIDATOR**.

| Check | Current state |
|---|---|
| AnalysisPlan/Pydantic schema | Enforced |
| Non-empty steps and unique IDs | Enforced |
| Tool allowlist and MVP stage | Enforced |
| Credential-like param keys | Rejected |
| Registered params JSON Schema | Enforced |
| Known expected artifact/ref enums | Enforced syntactically |
| Expected artifact belongs to named producer step | Not enforced |
| Step output types allowed by selected tool | Not enforced directly |
| Resource existence/kind | Not in PlanValidator |
| DataProfile/readiness/semantic eligibility | Not enforced |
| Tool/resource caps | Only indirectly when encoded in params schemas or adapter limits |
| Max steps/duplicate tool calls | Not enforced |
| Dependency graph/artifact producer-consumer binding | Not supported |

Invalid tool IDs and unsafe/unknown params are stopped before persistence.
Scientifically incompatible but schema-valid tool choices generally fail later
at the API input-ref gate or adapter runtime.

## Parameter Selection

| Domain | Mechanism |
|---|---|
| Phase 10K ML | Profile 2.0 semantic groups and deterministic object binding |
| Composition Space/Dataset Explorer | Profile objects/readiness plus fixed bounded defaults |
| Older ML/table/viz | Prompt markers, column-name heuristics, then first compatible columns/defaults |
| Structure/BZ/trajectory/phonon/volumetric | Fixed approved params after resource and phrase checks |
| Live LLM | Model chooses from parameter names and shallow Profile context; validator checks JSON Schema |

Ambiguous Profile 2.0 ML semantics route to Dataset Explorer diagnostics when
the matching ambiguity rule fires. There is no clarification request. Other
ambiguous choices are resolved by deterministic ordering, the first eligible
object/group/column, or the generic fallback.

## Representative Prompt Probe

All probes used MockLLMProvider and committed Profile fixtures; no provider or
network was contacted.

| Prompt category | Current result | Main gap |
|---|---|---|
| Elements and chemical systems | `dataset.materials_explorer` | Coherent product choice, but no composed element/system-specific plan |
| Broad structure reasonableness | `structure.summary` | Cannot plan coordination/RDF/XRD/viewer combination or explain scientific sufficiency |
| Materials with poor predictions | `ml.basic_metrics` | Phrase misses product-level regression route and loses sample/chemistry diagnostics |
| Trustworthiness of uncertainty | `ml.basic_metrics` | Phrase misses uncertainty evaluator despite ready Profile data |
| Broad phonon quality check | `ml.basic_metrics` | No broad phonon diagnosis intent; fallback is resource-incompatible |
| Charge-density features | `structure.volumetric_data` | Correct bounded consumer preparation, but no result interpretation |
| Comprehensive dataset analysis | `dataset.materials_explorer` | One coherent product only; no capability-ranked multi-tool plan |
| `formation_energy` distribution | `viz.histogram` on `band_gap` | Correct tool class, but requested column is not reliably bound |

## Analysis Intent, Clarification, and Repair

There is no `AnalysisIntent` or equivalent structured goal object.
`PlannerRequest` contains only raw prompt, dataset ID, profile ID, and Registry
version. `AnalysisPlan.goal` repeats the raw prompt, so intent and executable
plan are not independently represented.

* Analysis Intent recommendation: **REQUIRED**.
* Clarification state/follow-up selection: **NOT_IMPLEMENTED**.
* Conversation history/previous correction: **NOT_IMPLEMENTED**.
* JSON/schema/scientific plan repair: **NOT_IMPLEMENTED**.
* Unbounded repair loop risk: absent because there is no repair loop.

## Frontend Planner UX

| Capability | State |
|---|---|
| Natural-language input and selected dataset/Profile | Ready |
| Generated plan, steps, developer params/refs | Visible |
| Validation errors | Visible and typed |
| Timeline, ToolCalls, artifacts, errors | Visible |
| Inspect before enqueue | Missing; create-and-run is one action |
| Edit/remove/reorder plan steps | Missing |
| Clarification/user selection | Missing |
| Cancel | Missing |
| Same-job retry | Missing; action creates a new job |
| Partial endpoint refresh | Present for result reads, not plan repair |

## Result Interpretation

Adapters and older deterministic report paths emit summaries, warnings,
recipes, and some next-step text. The current Planner path does not send
structured scientific results to an LLM and has no interpretation contract,
calculation-grounding guardrail, or bounded recommendation stage. Phase 10L-4
should therefore extend existing deterministic summaries rather than replace
them, using a strict structured result context and explicit no-invention rules.

## Security and Resource Audit

* Unknown tools, non-MVP tools, credential-shaped params, and invalid params are rejected.
* The LLM has no adapter, shell, Python, filesystem, or scientific execution authority.
* BYOK values are resolved separately and are not serialized in plan params.
* Prompt/profile/tool descriptions are untrusted text; no explicit prompt-injection labeling separates those sources today.
* No artifact content is sent to the current planner; future interpretation must add an untrusted-content boundary.
* There is no plan step cap, prompt length cap, Registry serialization cap, or API upper bound for provider max tokens/temperature.
* Adapter and Registry execution caps still constrain actual scientific work.
* `NO_PHASE10L0_EXTERNAL_NETWORK_REQUESTS` and `NO_SECRET_PATTERN_HITS` are required closure markers.

## Terminology Freeze

* **Agent**: user-facing intelligent orchestration concept.
* **Planner**: component that generates an AnalysisPlan.
* **Runtime**: deterministic validated execution boundary.

This terminology recommendation does not rename source APIs.

## Evidence

Machine-readable audit captures are under
`docs/phase10l/evidence/phase10l0_agent_planner_capability_audit/`.
