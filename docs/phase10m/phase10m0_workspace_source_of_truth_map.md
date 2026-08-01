# Workspace Source-of-Truth Map

| Area | File/module | Current responsibility | User-visible entry | Data authority | Reusable for 10M | Gap |
|---|---|---|---|---|---|---|
| Frontend route | `apps/web/app/page.tsx` | Renders `PlannerWorkbench` | `/` | none | preserve as analysis entry | no Workspace route |
| PlannerWorkbench | `apps/web/app/components/PlannerWorkbench.tsx` | End-to-end single-page orchestration | `/` | API projections | shell components | in-memory only |
| Job timeline | `PlannerWorkbench.tsx` | SSE/polling event timeline | Agent process tab | `job_events` | yes | no history restore |
| Plan detail | `PlannerWorkbench.tsx`, planner API | Intent, selection, bindings, 0.1/0.2 Plan | conversation/plan tab | persisted Plan and L1/L2 records | yes | no independent deep link |
| Dependency graph | `DependencyExecutionPanel` | bindings, topological order, step/binding states | plan and results | Plan 0.2 plus execution record | yes | not a Workspace panel contract |
| ToolCall view | `ToolCallList` | status, params, provenance | results | `tool_calls` | yes | no focused ToolCall route |
| Artifact view | `ArtifactGallery` | grouped metadata and inert details | results | `artifacts` | partial | preview/download incomplete |
| Dataset product | `dataset-explorer/*` | typed dataset overview | results | typed `table_json` artifact | yes | local selection only |
| ML product | `materials-ml/*` | typed evaluation surfaces | results | typed ML artifact | yes | local selection only |
| Composition Space | `composition-space/*` | PCA/cluster product renderer | results | Adapter artifact | yes | local selection only |
| Structure viewer | `viewer-scene/*` | validated Three.js structure viewer | results | viewer-scene artifact | yes | no shared inspector contract |
| Trajectory viewer | `trajectory-viewer/*` | validated frame/playback surface | results | trajectory artifacts | yes | frame state not shareable |
| Phonon view | `phonon-*` | band, DOS, animation, combined views | results | phonon artifacts | yes | product-specific state |
| Brillouin view | `brillouin-zone/*`, `band-bz-link/*` | reciprocal scene and exact linked selection | results | BZ/phonon artifacts | yes | linkage is not global |
| Volumetric view | `volumetric-viewer/*` | validated field, isosurface, slice, volume | results | volumetric artifacts | yes | large payload lifecycle not centralized |
| Interpretation | `GroundedInterpretationPanel` | claims, limits, recommendations | results | persisted interpretation | yes | no Workspace findings route |
| Evidence drill-down | same panel and interpretation API | exact evidence refs | claim details | persisted evidence bundle | yes | no cross-panel inspector |
| Report | `reports` table/repository, report artifacts | generated immutable report records | static results preview | Report repository | partial | no composition/read API |
| Recipe | `visualization_recipes` repository, Recipe artifacts | reproducibility record | static results preview | Recipe repository | partial | 0.2 dependency closure absent |
| API | `apps/api/mdi_api/main.py`, `routers/planner.py` | job-scoped read APIs | frontend client | repositories | yes | no aggregate Workspace/history API |
| Repository | `repositories.py` | InMemory and SQLAlchemy persistence | none | PostgreSQL/SQLite/in-memory | yes | no Workspace repository |
| Persistence | migrations `0001`-`0006` | Job-centered source records | none | database | yes | no Workspace tables |
| Browser runners | `apps/web/test/*browser-evidence.mjs` | product-specific captured replay | test only | sanitized fixtures/current UI | partial | no consolidated Workspace runner |

## Ownership seal

**REVIEWER-SEALED RECOMMENDATION**

Workspace owns navigation, panel descriptors, user layout state, pinned canonical selection, recovery revisions, and source references. It does not own or copy Profile, Intent, Plan, Job, ToolCall, Artifact, evidence, interpretation, Report, or Recipe scientific content.
