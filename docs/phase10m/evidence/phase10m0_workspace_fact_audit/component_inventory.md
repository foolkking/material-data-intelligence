# Current Component Inventory

Audit baseline: `8f304fa08ddab1cefd69848f621f8438fc2038d5`.

| Area | Current owner | Fact |
| --- | --- | --- |
| Unified shell-like surface | `apps/web/app/components/PlannerWorkbench.tsx` | One large in-memory single-page orchestration surface |
| Data context | PlannerWorkbench data rail | Dataset/Profile context; no persisted Workspace state |
| Plan/capability | PlannerWorkbench panels | Intent, eligibility, selection, bindings, plan |
| Execution | PlannerWorkbench timeline/dependency panels | Job events, ToolCalls, graph and lineage |
| Artifact gallery | PlannerWorkbench artifact region | Typed products plus generic inert fallback |
| Dataset | `dataset-explorer/*` | Product-specific current renderer |
| Materials ML | `materials-ml/*` | Product-specific current renderer |
| Composition | `composition-space/*` | Product-specific current renderer |
| Structure | `viewer-scene/*` | Current Three.js renderer and exact local selection |
| Trajectory | `trajectory-viewer/*` | Current bounded frame renderer |
| Phonon | `phonon-*/*` | Current band, DOS, band-DOS and animation renderers |
| Brillouin | `brillouin-zone/*`, `band-bz-link/*` | Current exact reciprocal mapping in local component scope |
| Volumetric | `volumetric-viewer/*` | Current slice/volume/field products |
| Interpretation | PlannerWorkbench findings/evidence region | Grounded claims and evidence drill-down |
| Report/Recipe | PlannerWorkbench report/recipe summary | Existing records/artifacts shown without composition product |

There is no checked-in Workspace panel contract, renderer registry, global selection context, saved layout component, or Workspace route component.
