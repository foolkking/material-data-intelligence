# Release Architecture and Authority

The canonical flow is `DataProfile -> AnalysisIntent -> EligibilityResolution -> Planner -> AnalysisPlan -> PlanValidator -> QueueWorkerRuntime -> Adapter -> Artifact -> Grounded Interpretation -> ScientificWorkspace -> Report -> Recipe`.

| Layer | Authority |
|---|---|
| Data/Profile | exact project, dataset version, resource IDs and hashes |
| Planner | structured JSON AnalysisPlan only; no arbitrary Python, shell, filesystem, or network execution |
| Runtime | persisted Plan, Tool Registry validation, queue worker, registered Adapter |
| Science | registered Adapter output persisted as checksum-bound Artifact |
| Workspace | one server-owned Workspace per Job; URL owns active panel/exact shareable selection; memory owns transient view state |
| Viewer | exact Artifact type/version to inert typed renderer; no frontend scientific recomputation |
| Report | deterministic composition of persisted facts; no scientific recomputation |
| Recipe | exact declarative replay manifest with no Plan, Job, queue, ToolCall, or execution authority |

`localStorage` and `sessionStorage` are not canonical scientific Workspace authority. Artifact count is not panel count: logical result surfaces and the exact Artifact Gallery keep every Artifact reachable while `MAX_PANELS_PER_WORKSPACE=32` remains enforced.
