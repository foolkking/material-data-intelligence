# Behavior Invariants

**Previous freeze:** `FROZEN_BASELINE_V1`
**Current:** `FROZEN_BASELINE_V2`
**Amendment date:** 2026-09-06
**Freeze status:** `ARCHITECTURE_FREEZE_AMENDED_PENDING_BASELINE_COMMIT`

V2 separates immutable behavior and UX semantics from current implementation geometry. Values in section C are comparison evidence, not a permanent acceptance floor.

## A. HARD_BEHAVIOR_INVARIANTS

### Identity and authority

- API URLs/methods/contracts, route/query/redirect identities, authorization and error semantics remain unchanged.
- Database schema, Alembic filenames/revision IDs/parentage, and persisted identifiers remain unchanged.
- ScientificObject, immutable Version, Result, Artifact, Recipe and Report identities/authority remain unchanged.
- Adapter identity/scientific authority, Tool Registry identity/validation, queue names, worker roles and scientific semantics remain unchanged.
- Exact object/version selection remains fail-closed; a missing immutable version cannot silently fall back.
- Runtime topology and PostgreSQL/Redis/MinIO authority are not changed by source relocation.

### Execution and security

- Long parse, planning, visualization, render, export and report operations remain asynchronous where currently required.
- Tool execution authority remains in the backend validated Tool Registry, queue and execution runtime.
- LLM outputs that influence product state remain role-bounded, versioned, schema-constrained, validated, non-executable by themselves, and persisted/auditable where current contracts require it.
- Planner, Orchestrator, Interpreter and Report Composer may retain their distinct existing structured output contracts.
- LLM roles do not receive arbitrary Python, shell, filesystem, unrestricted network, direct database, direct queue, or Tool execution authority.
- Secrets/BYOK values do not enter prompts, logs, artifacts, recipes, reports or exports.
- Agent Timeline exposes structured process records, not hidden chain of thought.

### Queue and dynamic identity

The following remain resolvable through canonical implementations or old-path shims:

- `mdi_api.research_agent_worker.run_queued_turn`
- `mdi_api.research_agent_planning_worker.run_queued_planning`
- `mdi_workers.queue_runtime.run_queued_job`
- `mdi_api.scientific_results.worker.run_queued_result_projection`
- `mdi_workers.interpretation_worker.run_queued_interpretation`
- `mdi_workers.report_worker.run_queued_report_generation`

Queue names remain `mdi-agent-turns`, `mdi-agent-plans`, `mdi-jobs`, `mdi-agent-results`, `mdi-agent-interpretations`, and `mdi-agent-reports`.

## B. UX_SEMANTIC_INVARIANTS

### Global

- Product route/session/selection identity survives layout and source changes.
- Keyboard, focus, permission, loading, empty, failure and recovery semantics do not regress.
- The Phase 9C product semantics remain: global context, collapsible/zoomable data context, and one active main-workspace tab.
- Frontend remains presentation/orchestration, never execution authority.

### Research

- Conversation and Scientific Workbench remain distinct accessible work contexts.
- Empty, asking/history, planning, running, result/viewer, loading and failure states remain semantically distinct.
- Recent-window/expanded bounded history must not regress to an unbounded DOM; current earlier/newer and history-location capabilities remain available.
- Session, turn, result, dataset and route identities survive pane/layout transitions.
- Narrow/mobile offers a compact or single-pane equivalent that exposes both Conversation and Workbench completely.
- Pane switching preserves necessary reading position and focus context.
- Scientific result/workbench content keeps its scientific authority.

### Data

- Dataset/ScientificObject/Version navigator context and exact selection remain available.
- Main scientific workbench and optional detail/inspector capability remain available.
- Empty, importing, import failure, object selection, version selection and viewer states remain distinguishable.
- Table, structure, trajectory, phonon, electronic and volumetric viewer semantics remain intact.

### Scroll semantics

- Every archetype has one explicit scroll-ownership model; accidental nested page scrolling is prohibited.
- Body/root/pane ownership and sticky header/composer behavior must be deterministic.
- Zoom must not create an unintended third scroll owner.
- Independent Research pane scrolling is permitted but is not mandatory if an equivalent, explicit model preserves state, focus and readability.

## C. CURRENT_IMPLEMENTATION_BASELINES

These are `CURRENT_OBSERVED_GEOMETRY` or `CURRENT_INTERACTION_BASELINE`, not immutable requirements:

| Area | Current baseline | Freeze meaning |
|---|---|---|
| Research conversation sizing | 36% base, about 420px default, 320–640px clamp | before/after comparison only |
| Research splitter | about 7px with keyboard/pointer separator behavior | separator accessibility is semantic; exact width is not |
| Research desktop scroll | independently scrolling conversation/workbench | current interaction baseline, replaceable by an explicit equivalent |
| Research breakpoint | current fixed media-query transition | not frozen numerically |
| Data navigator | about 264px | not frozen numerically or permanently visible |
| Data inspector | about 344px when present | optional capability; not a permanent column |
| Data pane ratios/collapse | current grid and thresholds | not frozen |
| Global shell | observed about 56px/44px layers | current geometry only |
| History DOM | recent window; expanded cap currently 100 | boundedness is invariant; exact cap is tunable with approval |

## Acceptance

Each future batch records PASS/FAIL/NOT_VERIFIED for applicable hard and semantic invariants. Geometry may intentionally change only in a separately approved UI implementation, with explicit readability, focus, zoom, state and scroll verification. Source migration alone must not intentionally change geometry.
