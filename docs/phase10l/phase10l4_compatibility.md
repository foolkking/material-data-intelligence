# Phase 10L-4 Compatibility

Phase 10L-4 is additive. AnalysisIntent remains 1.0, EligibilityResolution
remains 1.0, and AnalysisPlan remains 0.1/0.2. Plan hashes, dependency binding,
QueueWorkerRuntime execution, Registry/Adapter authority, Job status, ToolCall,
Artifact, and lineage semantics are unchanged.

Historical jobs and artifacts remain readable. Formal interpretation requires
terminal exact source integrity; unsupported historical Artifact contracts
return `NO_SUPPORTED_EVIDENCE` rather than being guessed.
