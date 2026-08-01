# Phase 10L-5 Natural-Language Evidence Architecture

Status: IMPLEMENTED; awaiting exact-SHA CI and verified queue archive.

Phase 10L-5 closes the product path from a frozen natural-language goal to a
real persisted scientific result. The canonical path is:

```text
raw goal
 -> exact DataProfile 2.0
 -> AnalysisIntent 1.0
 -> EligibilityResolution 1.0
 -> capability selection and exact binding
 -> AnalysisPlan 0.1 or 0.2
 -> persisted Job / QueueWorkerRuntime
 -> registered Adapter artifacts and lineage
 -> ScientificEvidenceBundle
 -> grounded interpretation
```

Interpretation is post-execution and read-only. It cannot create a plan, Job,
ToolCall, queue message, artifact, or Runtime action. Artifact content is inert
data. The L5 live gate replays all five frozen user goals through the real
DeepSeek provider; deterministic and fake paths remain default-CI test paths.

No Planner, Runtime, Registry, AnalysisPlan, dependency, or scientific
algorithm redesign is included in this phase.
