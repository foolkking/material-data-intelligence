# Current API Inventory

Audit baseline: `8f304fa08ddab1cefd69848f621f8438fc2038d5`.

Current Planner read surfaces include exact Job, event/SSE, ToolCall, Artifact metadata/content, result, AnalysisPlan, dependency execution/lineage, interpretation, and evidence routes under `apps/api/mdi_api/main.py`. Dataset/Profile and provider/secret-management routes support analysis creation.

Confirmed absences:

- no Workspace create/read/update/list API;
- no atomic metadata-first Workspace snapshot;
- no project Job history route despite repository `list_by_project` support;
- no report composition product API;
- no recipe composition/reviewed replay product API.

Artifact content access remains bounded and Job-scoped, validates size/hash/media type, and sends no-store/nosniff controls. Proposed Workspace APIs do not replace this authority.
