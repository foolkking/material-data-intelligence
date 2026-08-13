# Canonical Product API Reference

The FastAPI route registry in `apps/api/mdi_api/main.py` is the route authority. Examples use sanitized IDs.

| Concern | Routes |
|---|---|
| Dataset/import/Profile | `POST /datasets/upload`, `GET/POST /datasets/{dataset_id}/profile` |
| Intent/clarification | `POST /planner/intents`, `POST /planner/intents/{intent_id}/clarification` |
| Eligibility/Plan | `POST /planner/preview`, `POST /planner/validate`, `GET /planner/analysis-plans/{plan_id}` |
| Job/Runtime | `POST /planner/jobs`, `GET /planner/jobs/{job_id}`, events, ToolCalls, dependencies, Artifacts, result |
| Artifact | `GET /artifacts/{artifact_id}`, download, exact Job Artifact content |
| Workspace | `POST/GET/PATCH /workspaces...`, panels and layout revisions |
| Report/Recipe | source inventory, preview, finalize/list/get, Recipe and export under `/workspaces/{workspace_id}/report-compositions...` |

Typed errors include unsupported input, clarification required, capability mismatch, stale source, cross-project rejection, XRD wavelength mismatch, generic phonon mapping-only disposition, and `PANEL_CAP_EXCEEDED`. Clients must not bypass these by injecting Tool IDs, selecting latest resources, ignoring checksums, forcing Plan 0.2, or skipping PlanValidator.

IDs in examples are placeholders such as `project_example`, `dataset_example`, and `workspace_example`; credentials, private paths, signed storage URLs, and test-only routes are excluded.
