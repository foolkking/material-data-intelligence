# Phase 10L-3 Compatibility

## Preserved Contracts

- AnalysisIntent remains `1.0`.
- EligibilityResolution and CapabilityDecision remain `1.0`.
- ToolPlannerMetadata `1.0` remains valid for independent planning.
- ToolArtifactPortMetadata `1.1` is an additive overlay.
- AnalysisPlan `0.1` remains valid and unchanged.
- Historical 0.1 plan hashes are not recomputed as 0.2 hashes.
- Existing tool parameter schemas and execution authority remain Registry
  controlled.
- Existing PlanValidator remains required and is not weakened.
- Existing 0.1 QueueWorkerRuntime behavior remains its independent step loop.
- Historical jobs and artifacts remain readable.

## New 0.2 Behavior

Only a canonical capability-aware request with an exact compatible artifact
pair may produce 0.2. Its plan/binding/execution/lineage associations remain
external to historical 0.1 records. Runtime branches on exact schema version;
it does not infer a version from step count or list order.

The existing Job status vocabulary already includes `partial_success`; 0.2
uses it when at least one branch succeeds and another fails or is blocked.
Detailed meaning is owned by `DependencyExecutionRecord 1.0`.

## Legacy API

Legacy requests keep their documented compatibility path and are not counted
as Phase 10L-3 dependency coverage. A canonical 0.2 failure does not fall back
to legacy planning or independent 0.1 execution.

## Regression Obligations

Closure must prove unchanged 0.1 single- and multi-step execution, historical
hashes, jobs, artifacts, Phase 10K products, Phase 10L-1 clarification, Phase
10L-2 exact selection/binding, Registry authority, and service-backed behavior.
Those checks are not declared PASS by this document.
