# Phase 10M-0 Workspace Information Architecture

Status: REVIEWER-SEALED RECOMMENDATION
Production status: NOT IMPLEMENTED

## Primary navigation

The root route `/` remains the analysis-entry `PlannerWorkbench`. A persisted analysis opens at `/workspaces/{workspaceId}`. Successful canonical job creation exposes an explicit `Open workspace` command; project history exposes the same route. Back and forward navigation restore the active panel and validated URL selection without creating, rerunning, or mutating scientific work.

The Workspace header has these fixed fields: project and dataset/version, original goal, projected execution status, partial-result marker, DataProfile version, persisted-layout state, report/export entry, and provenance entry. Source hashes are available in the provenance panel and are not placed in the compact title row.

## Main regions

The desktop Workspace preserves the Phase 9C frame:

1. Global context header.
2. Collapsible and resizable data-context rail.
3. One active main workspace panel.
4. Workspace-local vertical secondary navigation inside the main region.
5. A contextual inspector rendered as an overlay drawer, never as a permanent third column.

The sealed panel groups and order are:

1. **Overview**: goal, source identities, status, partial/legacy/stale disclosures.
2. **Data**: DataProfile and source resource facts.
3. **Plan**: Intent, eligibility, exact bindings, plan, dependency graph.
4. **Execution**: Job, ToolCalls, event timeline, dependency execution.
5. **Results**: typed scientific artifact panels and inert fallbacks.
6. **Findings**: grounded claims, warnings, limitations, recommendations.
7. **Evidence**: evidence items, claim links, and artifact lineage.
8. **Provenance**: immutable source hashes, versions, and audit JSON.
9. **Report**: persisted report composition and export state.

Only one group panel is active. Results may contain a bounded panel stack, but it does not create nested navigation cards or a graph editor.

## Inspector

`WorkspaceSelectionContext 1.0` is the inspector input. The inspector supports exact artifact, sample/material object, structure/site/atom, trajectory atom/frame, phonon q-point/branch, reciprocal point, volumetric field, evidence-item, and claim identities. Unsupported mappings show `NOT_APPLICABLE`; they never guess by array position or display label.

## Mobile

At 390x844, the header becomes a two-row compact status header, data context becomes a left drawer, secondary navigation becomes an accessible panel switcher, and exactly one panel is displayed. The inspector is a bottom sheet. Dependency tables and provenance rows use stacked key/value records. Fullscreen scientific views use their existing explicit fullscreen command and retain a text fallback.

## Route and deep-link contract

Canonical route:

```text
/workspaces/{workspaceId}?panel={panelId}&selection={boundedSelectionToken}
```

- `workspaceId` is a stable server identity.
- `panel` must name a panel in the current snapshot.
- `selection` is base64url canonical JSON for `WorkspaceSelectionContext 1.0`, at most 2,048 bytes.
- Unknown, stale, foreign-project, or incompatible values are rejected and removed from the effective state.
- Camera position, hover, animation time, and temporary filters never enter the URL.

This structure is sealed by M-D006, M-D015, M-D021, and M-D023.
