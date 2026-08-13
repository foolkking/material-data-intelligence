# Phase 13 Initial Release Scope

The Initial Release is a Material Data Intelligence and Scientific Visualization Platform. The product chain is Resource/Upload -> DataProfile -> AnalysisIntent -> bounded clarification -> EligibilityResolution -> capability-aware Planner -> AnalysisPlan 0.1/0.2 -> PlanValidator -> QueueWorkerRuntime -> registered Adapter -> persisted Artifact -> Grounded Interpretation -> ScientificWorkspace -> Finding/Evidence/Provenance -> Report -> non-executable Recipe.

Support, scientific validation, cross-platform reproducibility and presentation validation remain separate. Future Scope and Not Planned work are outside this release. Bounded clarification remains one round, at most three questions, with typed `CLARIFICATION_NOT_ALLOWED` on a second-round attempt.

The current superseding Scope Baseline is `bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba`. It incorporates the existing product-entry corrections and exactly two reviewer-authorized bounded typed input rows for `PhononBand` and `PhononDos`; generic phonon YAML/JSON remains `MAPPING_ONLY`, and scientific validation and Tool capability scope are unchanged. The prior `f188b3e15aa94111787297ffde07b37f90cfdd1fe4e910e39f941e956b455455` baseline remains historical and superseded.
