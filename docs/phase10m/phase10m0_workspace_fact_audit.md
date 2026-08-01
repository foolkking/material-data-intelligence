# Phase 10M-0 Workspace Fact Audit

## Audit result

**CONFIRMED CURRENT FACT**

`CURRENT_WORKSPACE_LEVEL = WORKSPACE_LIKE_SINGLE_PAGE`.

The root route renders `PlannerWorkbench`. It combines dataset context, planning, execution, results, scientific viewers, grounded interpretation, evidence, artifact inventory, and static Report/Recipe previews in one three-tab page. It is not a formal Unified Scientific Workspace because it has no Workspace entity, route identity, aggregate snapshot, history entry, saved layout, recovery contract, or global cross-artifact selection context.

`PHASE_10M0_AUDIT_READINESS = READY`.

## Repository baseline

| Fact | Value |
|---|---|
| Branch | `master` |
| Initial HEAD / origin | `8f304fa08ddab1cefd69848f621f8438fc2038d5` |
| Worktree | clean |
| L5 implementation | `bfc43bd39d7cc2fa319b9e88f9a4d37eec57ee37`, CI `30693848581` success |
| L5 completion | `e4b0a8f5619cbb1001ef64809db6400729a99d8d`, CI `30694747664` success |
| L5 archive | `8f304fa08ddab1cefd69848f621f8438fc2038d5`, CI `30695065220` success |
| Migration head | `0006_phase10l4_interpretation` |
| Registered tools | 53 total; 38 Planner-visible |
| Active task blocks | 0 |
| Phase 10M source implementation | absent |

## Current product flow

**CONFIRMED CURRENT FACT**

1. `/` loads health, datasets, provider catalog, and provider status.
2. The user selects, uploads, or creates a demo dataset and loads DataProfile 2.0.
3. A natural-language request enters the canonical Intent and capability-aware Planner path.
4. A ready result creates a persisted Plan and Job; non-ready outcomes create neither.
5. The page reads Job, events, ToolCalls, Artifacts, compact result, and dependency audit as six independent slices.
6. SSE updates the timeline; polling is the fallback.
7. Terminal Jobs expose deterministic or strict-provider interpretation and evidence.
8. Report and Recipe artifacts appear as static summaries and inert previews.

## Current surfaces and limits

| Concern | Current fact | Current limitation |
|---|---|---|
| Navigation | One root page, three mutually exclusive main tabs | No Workspace/history/deep-link route |
| Analysis context | Dataset/Profile, raw goal, Intent, eligibility, decision, exact bindings, Plan | Context is tied to current in-memory submission |
| Execution | Job timeline, ToolCalls, 0.2 graph, partial execution, lineage | No job history UI, cancel UI, or manual retry UI |
| Results | Product-specific renderers plus Artifact Gallery | Gallery preview/download controls are not a complete typed panel system |
| Interpretation | Findings, warnings, limitations, recommendations, evidence drill-down | Projector coverage is 12 tool/artifact combinations, not all artifacts |
| Report | Job-bound table/repository and report artifacts | No report composition API or product workflow |
| Recipe | Job-bound table/repository and Recipe 0.1 artifacts | No dependency-complete Workspace recipe product or rerun review flow |
| Recovery | Persisted Job graph is readable by exact ID | No route or persisted UI state restores it |
| Selection | Exact local selections exist in individual product composites | No Workspace-wide selection authority |

## Browser and runtime audit

**CONFIRMED CURRENT FACT**

- A new current-code replay covered Chromium, Firefox, WebKit, and Chromium `390x844` using persisted sanitized captures.
- The replay made zero live API calls and zero LLM calls, and recorded zero unapproved external requests, console errors, page errors, or document-level horizontal overflow.
- The replay covered five ready families and clarification, unsupported, and capability-mismatch states.
- The committed L3 dependency runner is historical and fails current replay because it does not intercept the later interpretation read route. Current partial/blocked facts are therefore cross-checked through current component tests, current source, and a Phase 10M-0 dedicated capture rather than claimed from that old runner.

This is a fact audit, not a new product acceptance claim.

## No duplicate scientific authority

`FRONTEND_DUPLICATE_SCIENTIFIC_AUTHORITY = NONE`.

Frontend code validates contracts, maps persisted values, formats values, sorts/paginates display data, performs renderer-local coordinate transforms, camera operations, selection mapping, bounded visualization sampling, and local measurements explicitly classified as display state. It does not persist those values as Adapter-equivalent scientific results. Formal results remain:

```text
Registered Adapter -> QueueWorkerRuntime -> persisted Artifact -> validated mapper
```

Phase 10M must preserve this boundary. Renderer-local measurements and exports remain labeled as local display-derived data unless a separately approved Adapter persists them.

## Readiness

No source change is required to complete this audit. Current Job-centered persistence and lineage are sufficient to define a lazy Workspace projection. Phase 10M-1 requires reviewer approval and a separate executable prompt.
