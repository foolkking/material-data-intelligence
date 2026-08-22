# Research Execution Summary v1

`ResearchExecutionSummary` is an immutable deterministic projection of one
terminal Agent 2.0 execution. The authority remains the existing `Job`,
`ToolCall`, `Artifact`, `JobEvent`, persisted AnalysisPlan, and CapabilityPlan.

Revision `0020_agent2_execution_integration` creates
`research_execution_summaries`. Both `research_turn_id` and `job_id` are unique,
so one Turn has at most one execution Job and one terminal summary. A replay
with the same source fingerprint returns the stored row; a different
fingerprint raises `EXECUTION_SUMMARY_CONFLICT`.

The `1.0` contract stores exact Turn/Plan/Job identity, `SUCCESS`, `PARTIAL`,
`FAILED`, or `CANCELED`, capability-level step status, declared output Artifact
refs, warnings, timestamps, projector version, and source fingerprint. The
fingerprint hashes stable sorted Job/ToolCall/Artifact/JobEvent facts. Summary
Artifact refs include only outputs declared by the immutable AnalysisPlan;
debug and undeclared runtime files remain persisted but are not product output.

`SUCCESS` requires every persisted Plan step to have a successful ToolCall.
`PARTIAL` requires a successful required step with a declared usable output and
an incomplete or failed required path. A terminal execution without usable
required work is `FAILED`. Job cancellation must be confirmed by the existing
runtime before the outcome becomes `CANCELED`.

`SUCCESS` and `PARTIAL` move the Turn to `RESULT_PENDING`, not `COMPLETED`.
Phase 4 creates no `ScientificResultSnapshot` and no assistant final message.
