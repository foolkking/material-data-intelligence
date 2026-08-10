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
