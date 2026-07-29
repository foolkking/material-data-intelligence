# Phase 10L-0 Agent / Planner Gap Matrix

Classification terms follow the Phase 10L-0 gate: `READY`,
`REUSABLE_FOUNDATION`, `PARTIAL`, `MISSING_10L`, `DEFER_10M`, `DEFER_10N`,
`FUTURE`, and `NOT_NEEDED`.

| Capability | Current implementation | Evidence | Status | Target |
|---|---|---|---|---|
| Raw user goal | `PlannerRequest.user_prompt`; repeated in `AnalysisPlan.goal` | Provider and schema code | REUSABLE_FOUNDATION | 10L-1 |
| Structured Analysis Intent | No separate object, targets, constraints, or desired outputs | Schema search | MISSING_10L | 10L-1 |
| DataProfile transport | Typed Profile passed to both providers | Planner API/provider protocol | READY | Retain |
| Mock Profile awareness | Strong for K3/K4; partial elsewhere | Routing predicates and probes | PARTIAL | 10L-2 |
| LLM Profile awareness | Shallow table/structure summary only | `planner_prompt.py` | MISSING_10L | 10L-2 |
| Tool execution metadata | Inputs, params, outputs, limits, timeouts | RegisteredTool/loader | READY | Retain |
| Planner-facing eligibility metadata | No machine-readable semantic requirements/readiness mapping | Registry inventory | MISSING_10L | 10L-2 |
| Tool ranking/collision policy | Fixed Mock priority; LLM prompt has no ranking hints | Provider chain/prompt | MISSING_10L | 10L-2 |
| Deterministic single-tool plan | Many tested routes | Existing planner tests | READY | Retain |
| Profile-bound product plans | Dataset, ML, Composition Space | Phase 10K tests/evidence | READY | Retain |
| Broad intent planning | Usually one first-match or generic fallback | Prompt probe | MISSING_10L | 10L-2 |
| Parameter binding | Exact for K3/K4; heuristic/default elsewhere | Provider helpers/probe | PARTIAL | 10L-2 |
| Semantic ambiguity handling | Diagnostic fallback for selected K3 ambiguity only | Provider code/K5 evidence | PARTIAL | 10L-1/2 |
| Clarification | No typed state or follow-up question | API/UI search | MISSING_10L | Reviewer decision |
| Multi-step schema | Ordered step array with unique IDs | AnalysisPlan/Validator | REUSABLE_FOUNDATION | 10L-3 |
| Sequential multi-step execution | Executes independent steps in order | Queue runtime/Band-BZ test | REUSABLE_FOUNDATION | 10L-3 |
| Explicit dependencies | None | AnalysisPlan schema | MISSING_10L | 10L-3 |
| Prior-step artifact binding | Ref type exists, producer binding/runtime injection do not | Schema/runtime | MISSING_10L | 10L-3 |
| Failure isolation | Prior artifacts persist; later steps stop; job fails | Queue runtime | PARTIAL | 10L-3 |
| Cancellation | Job statuses exist but this runtime has no cancellation check | Runtime/worker README | MISSING_10L | 10L-3 or later |
| PlanValidator schema/Registry gate | Strict schema, MVP allowlist, params, credential checks | Validator tests/code | READY | Retain |
| Profile/resource semantic validation | Outside PlanValidator; partial API object-ref check | Validator/API code | MISSING_10L | 10L-2/3 |
| Plan complexity caps | No max steps/duplicate calls/prompt cap | Validator/API code | MISSING_10L | 10L-2/3 |
| JSON parse handling | Safe rejection of non-object/non-JSON | Provider/API tests | READY | Retain |
| Plan repair | No schema/scientific retry loop | Provider/API code | MISSING_10L | Reviewer decision |
| Real provider isolation | Explicit opt-in; default Mock; keys resolved at call time | Provider/API tests | READY | Retain |
| Plan persistence/hash | Persisted before execution; canonical hash/job binding | Repository/runtime tests | READY | Retain |
| Planner reproducibility metadata | Provider stored; model/prompt version/config absent | Repository record | PARTIAL | 10L-2 |
| Plan preview UI | Plan visible after create/enqueue | PlannerWorkbench | PARTIAL | DEFER_10M |
| Plan editing/approval/cancel UX | Absent | PlannerWorkbench | DEFER_10M | 10M |
| Timeline/calls/artifacts | Structured UI and API reads | PlannerWorkbench/API | READY | Retain |
| Deterministic summaries/recipes | Adapter outputs and legacy report paths | Artifact inventory | REUSABLE_FOUNDATION | 10L-4 |
| LLM result interpretation | Absent | Repository search | MISSING_10L | 10L-4 |
| Grounded findings guardrail | No interpretation contract yet | Repository search | MISSING_10L | 10L-4 |
| Natural-language E2E evidence | Tool-specific evidence exists; broad Agent cases do not | Existing evidence | MISSING_10L | 10L-5 |
| Professional tool coverage | Deferred to approved Phase 10N | Canonical roadmap | DEFER_10N | 10N |
| Full conversational memory | Not present and not required for bounded initial planning | API/UI | FUTURE | Future |
| Generic workflow engine/DAG product | Explicitly outside scope | Product requirements | NOT_NEEDED | None |
| Arbitrary code execution | Prohibited and absent | Architecture/security boundary | NOT_NEEDED | None |

## Maturity Assessment

| Level | Definition | Current assessment |
|---|---|---|
| 0 | Manual tool execution | Exceeded |
| 1 | Keyword routing | Exceeded but still heavily used |
| 2 | Structured single-tool planning | Ready |
| 3 | Data/profile-aware tool selection | **Current level, uneven by domain** |
| 4 | Capability-aware multi-tool planning | Missing |
| 5 | Bounded interpretation and repair | Missing |

The Level 3 rating is based on real Phase 10K semantic-group/readiness use,
not merely on the presence of a Profile argument. It does not imply that all
domains consume Profile 2.0 consistently.
