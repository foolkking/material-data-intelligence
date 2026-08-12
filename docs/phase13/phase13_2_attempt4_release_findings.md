# Phase 13-2 Attempt 4 Release Findings

## P13-R4-001

`P0 / RELEASE_CRITICAL_INTEGRATION_DEFECT / OPEN_REVIEWER_ACTION_REQUIRED`

The sealed Demo 1 contract requires Dataset Intelligence and Composition Space.
Its current canonical phrase, "show how the compositions are distributed", is
formally classified by AnalysisIntent as `composition_analysis`, not
`composition_space`. Production rules permit Composition Space only for an
explicit composition-space, embedding or clustering goal. The fresh Plan and
execution therefore selected only `dataset.materials_explorer` and omitted the
required `dataset.composition_space` and `plotly_json` output.

## P13-R4-002

`P0 / RELEASE_CRITICAL_INTEGRATION_DEFECT / OPEN_REVIEWER_ACTION_REQUIRED`

The current Planner produced AnalysisPlan 0.1 for Demo 1. Workspace authority
marks every 0.1 source `LEGACY_READ_ONLY`, and the real Workspace Report UI
disables Finalize for read-only workspaces. Consequently the normal user path
cannot finalize the required immutable Report and paired Recipe. Direct API
finalization is diagnostic evidence only and cannot substitute for the UI path.

Both findings require reviewer-authorized remediation outside Attempt 4.
