# Phase 10M-0 Decision Manifest

Canonical decision source: `docs/phase10m/phase10m_execution_lock.md`.

- M-D001 through M-D025: `SEALED_FOR_REVIEWER_APPROVAL`.
- Workspace entity: first-class persisted.
- Cardinality: one Workspace per Job.
- Source authority: references only; scientific payloads remain in current repositories/storage.
- Migration: YES, `0007_phase10m1_workspace_domain`, three tables.
- API: YES, bounded create/read/update/list/history routes.
- Route: `/workspaces/{workspaceId}`; `/` remains PlannerWorkbench.
- Panel contract: `WorkspacePanel 1.0` required.
- Selection: `WorkspaceSelectionContext 1.0` required.
- Historical Jobs: idempotent lazy projection; incomplete identity is read-only.
- Report/Recipe: reuse existing persistent ownership with additive versioned JSON contracts.
- Mobile: one panel, data drawer, panel switcher, inspector bottom sheet.
- Implementation sequence: Phase 10M-1 through 10M-7, each reviewer-gated.
- Production source in 10M-0: unchanged.
- Phase 10M-1 executable task: not created.
