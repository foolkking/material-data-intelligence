# Phase 12-2 Global Navigation + Planner / Agent Experience

Phase 12-2 changes product navigation presentation and Planner information
hierarchy while preserving existing routes, API authorities, DataProfile,
AnalysisIntent, EligibilityResolution, AnalysisPlan, QueueWorkerRuntime,
Artifact, Workspace, selection, Report and Recipe contracts.

The accepted global IA is `Home`, `Data`, `Analyses`, `Workspaces`, `Reports`,
and `Settings`. The implementation uses the existing Planner route and existing
dialogs/tabs/history API; it does not invent counts or unsupported destinations.

The Planner presents the user-facing path as data context, intent, plan,
execution and results. Exact IDs, tool bindings and raw JSON remain available in
Developer mode and are not the primary workflow language.
