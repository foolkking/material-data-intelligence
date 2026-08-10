# Phase 12 Implementation Backlog

| Phase | Goal | Allowed changes | Forbidden changes | Exit gate |
|---|---|---|---|---|
| 12-1 | Design System 2.0 | tokens, core components, visual language | navigation/authority redesign | 8 acceptance IDs, browser/mobile/a11y evidence |
| 12-2 | Navigation and Planner | app shell, Planner hierarchy, clarification, execution feedback | scientific/runtime semantics | 8 acceptance IDs and Planner journeys |
| 12-3 | Workspace and viewers | result-first Workspace, viewer chrome, chart/3D controls | scientific computation/geometry | 8 acceptance IDs and viewer matrix |
| 12-4 | Findings/Evidence/Inspector | trust path, layers, limitation presentation | provenance identity changes | 8 acceptance IDs and exact drilldown |
| 12-5 | Report/Recipe | source discovery, composition, readable Recipe | Recipe execution | 8 acceptance IDs and report/recovery flows |
| 12-6 | Responsive/accessibility | mobile, focus, reflow, alternatives | authority model changes | 8 acceptance IDs and browser/a11y closure |
| 12-7 | UX evidence closure | cross-product validation and remaining P0/P1 closure | new science | 8 acceptance IDs and Phase 13 handoff |

All phases require Registry 62, DataProfile 2.4, existing Runtime/Artifact/
Selection authority, zero frontend scientific recomputation, and no new dependency
or migration unless separately reviewer-authorized.

## 12-1 Execution Detail

Sources: `apps/web/app/globals.css`, existing shared native controls and
presentation-only `StatusLabel`. Allowed: semantic tokens, typography, density,
surface/focus/motion/status rules, component styling and representative shared
surface migration. Forbidden: Global/Workspace IA, Planner flow, viewer controls,
scientific colors/payloads, backend/API/schema/Registry/Profile/dependency changes.
Acceptance is `P12X1-A01` through `P12X1-A08`; the evidence manifest, browser
matrix, mobile/focus/contrast foundation and exact-SHA CI are required. 12-2 and
12-3 consume handoffs only after reviewer authorization.

## 12-2 Execution Detail

Sources: `PlannerWorkbench.tsx`, existing planner API client, message catalogs,
DS2 tokens and the Phase 12-1 navigation/Planner handoff. Allowed: global shell
navigation presentation, existing route/dialog/tab destinations, human-readable
Planner hierarchy, clarification context, execution stage feedback and typed
error recovery. Forbidden: new backend/API/schema authority, scientific or
runtime semantics, provider policy changes, browser scientific recomputation,
Workspace IA redesign or Phase 12-3 viewer work. Close only `UX-001` and
`UX-008`; retain all other owners. Acceptance is `P12X2-A01` through
`P12X2-A08`; deterministic navigation/planner evidence, browser/mobile replay,
accessibility and exact-SHA CI are required.

## 12-3 Execution Detail

Sources: `ScientificWorkspaceShell.tsx`, `WorkspaceArtifactGallery.tsx`, the
existing renderer registry, selection runtime, DS2 handoff and Phase 12-0
Workspace/viewer audit. Allowed: result-first presentation, presentation-only
Workspace grouping, shared result/viewer chrome, warning placement, exact
selection affordances, table alternatives and responsive viewer framing.
Forbidden: changing Workspace/API/schema identity, panel contracts, URL
selection semantics, renderer scientific values, lazy-loader authority,
scientific series colors, or frontend recomputation. Close only `UX-002` and
`UX-003`; all later-phase owners remain open. Acceptance is `P12X3-A01` through
`P12X3-A08`; evidence must include representative dense, chart, 3D, trajectory,
electronic, partial and failure states.

## 12-4 Execution Detail

Sources: `ScientificWorkspaceShell.tsx`, existing interpretation/evidence APIs,
Workspace Selection 1.0, the Phase 12-3 handoff and sealed claim/evidence
contracts. Allowed: persisted Finding hierarchy, exact evidence membership,
Evidence-to-Artifact source presentation, three-layer Inspector, provenance
chain presentation, warnings/limitations and responsive trust-path styling.
Forbidden: claim/evidence generation, confidence inference, scientific ranking,
fuzzy identity, lineage mutation, new LLM calls, Report/Recipe redesign or
backend/schema changes. Close only `UX-004`; later owners remain open.
Acceptance is `P12X4-A01` through `P12X4-A08`.

## 12-5 Execution Detail

Sources: `WorkspaceReportComposer.tsx`, existing Report composition API client,
ReportComposition/Recipe 1.0 contracts, Phase 12-4 trust-path handoff, and DS2.
Allowed: typed source eligibility explanation, exact selection/order/captions,
draft and preview hierarchy, explicit immutable finalization confirmation,
history/export presentation, and a human-readable Recipe before exact inert
JSON. Forbidden: Recipe execution, source inference, backend/API/schema changes,
scientific recomputation, and Phase 12-6 ownership. Close only `UX-005`.
Acceptance is `P12X5-A01` through `P12X5-A08`.

## 12-6 Execution Detail

Sources: Planner and Workspace shells, existing DS2 tokens, viewer table/text
alternatives, message catalogs, Phase 12-5 handoff and the sealed mobile
authority. Allowed: responsive/reflow corrections, keyboard/focus semantics,
skip navigation, dialog/drawer state, touch targets, contrast, forced colors,
reduced motion and terminology consistency. Forbidden: route/IA changes,
scientific recomputation, source/selection inference, backend/API/schema or
dependency changes, and Phase 12-7 ownership. Close only `UX-006` and `UX-009`.
Acceptance is `P12X6-A01` through `P12X6-A08`.
