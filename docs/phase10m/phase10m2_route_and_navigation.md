# Phase 10M-2 Route and Navigation

The additive route is `/workspaces/{workspaceId}`. The route parameter is the
only Workspace identity; no latest-Job or label lookup occurs. The active
panel is represented as `?panel={panelId}` and must match a visible panel in
the loaded Workspace snapshot. An unknown value produces a typed diagnostic
and no substitute selection.

Panel changes use browser history, so back, forward, refresh, and direct links
restore the exact active panel. The default is the current layout revision's
active panel, then the first deterministic visible panel. The nine navigation
groups remain Overview, Data, Plan, Execution, Results, Findings, Evidence,
Provenance, and Report.

PlannerWorkbench Workspace history uses `GET /projects/{projectId}/workspaces`
and performs no projection write. `Open Workspace` uses the sealed idempotent
`POST /workspaces` endpoint for the exact current Job before navigation.
