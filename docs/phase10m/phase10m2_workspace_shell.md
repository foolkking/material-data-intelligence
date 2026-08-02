# Phase 10M-2 Unified Scientific Workspace Shell

Status: IMPLEMENTED, exact-SHA lifecycle pending.

`/workspaces/{workspaceId}` now loads the exact persisted `ScientificWorkspace
1.0` metadata snapshot and presents the sealed nine-group Workspace
information architecture. `/` remains PlannerWorkbench and exposes both an
idempotent `Open Workspace` command for the current Job and a metadata-only
Project Workspace history entry.

The shell displays one active `WorkspacePanel 1.0` descriptor, exact source
status, bounded metadata, partial/legacy/stale/unsupported states, and inert
audit JSON. It does not request Artifact payloads, compute science, select
tools, execute recommendations, or create a new LLM call site.

M3 canonical selection propagation, M4 typed scientific renderers, M5 report
composition, and M6 recovery closure remain outside this implementation.
