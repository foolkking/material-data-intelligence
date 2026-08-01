# Current Route Inventory

Audit baseline: `8f304fa08ddab1cefd69848f621f8438fc2038d5`.

| Surface | Current route | Fact |
| --- | --- | --- |
| PlannerWorkbench | `/` | Only current Next page; renders the complete single-page workbench |
| Workspace | none | No `/workspaces/{id}` route exists |
| History | none | No user-visible Job or Workspace history route exists |
| Plan/Job/Artifact | none | Read through PlannerWorkbench APIs, not deep-linked pages |
| Interpretation/Evidence | none | Embedded inside PlannerWorkbench |
| Report/Recipe | none | Embedded inert summary only |
| Error/404 | framework default | No Workspace-specific source/legacy/stale route handling |

Source: `apps/web/app/page.tsx`, `apps/web/app/layout.tsx`, and route-file search under `apps/web/app`.

The complete proposed map is in `docs/phase10m/phase10m0_current_page_route_component_map.md`. This inventory is current fact, not implementation evidence for the proposed route.
