# Phase 13 Initial Release Scope

The Initial Release is a Material Data Intelligence and Scientific Visualization Platform. The product chain is Resource/Upload -> DataProfile -> AnalysisIntent -> bounded clarification -> EligibilityResolution -> capability-aware Planner -> AnalysisPlan 0.1/0.2 -> PlanValidator -> QueueWorkerRuntime -> registered Adapter -> persisted Artifact -> Grounded Interpretation -> ScientificWorkspace -> Finding/Evidence/Provenance -> Report -> non-executable Recipe.

Support, scientific validation, cross-platform reproducibility and presentation validation remain separate. Future Scope and Not Planned work are outside this release.

Bounded clarification means exactly the existing `AnalysisIntent 1.0` authority:
at most one clarification round, at most three questions, and typed
`CLARIFICATION_NOT_ALLOWED` on any second-round attempt.
