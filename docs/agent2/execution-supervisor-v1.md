# Execution Supervisor v1

Phase 4 adds a bridge around the existing runtime; it does not add another
Worker or execution model.

`ResearchExecutionDispatcher` accepts only `ANALYZE` or `CONTINUE_ANALYSIS`
Turns in `PLAN_READY`. It reloads the attached immutable AnalysisPlan and
CapabilityPlan, re-authorizes exact ScientificObjectVersion refs, creates one
existing Job, attaches it, and commits `QUEUED`. Redis/RQ publication occurs
after commit and carries only `job_id`. A failed publish is recoverable with the
same Job identity through `ResearchExecutionReconciler`.

Fresh Workers load Job and Plan from PostgreSQL. The existing
`DurableObjectStoreResolver` additionally hydrates UUID-shaped Agent 2.0 input
refs from the exact version's `normalized_payload_ref_json`, checks Project,
availability, bounded JSON size, and SHA-256, then registers that exact version
as the runtime source. It never follows `current_version_id`.

`ResearchExecutionSupervisor` reloads persisted Job, JobEvents, ToolCalls,
Artifacts, AnalysisPlan, CapabilityPlan, and Capability manifests. It projects
meaningful Turn events idempotently, classifies terminal execution, persists one
immutable summary, and synchronizes the Turn. Duplicate dispatcher and
supervisor delivery is safe.

Cancellation changes `QUEUED` or `RUNNING` to `CANCELING`, records the request,
and delegates authority to the existing Job `cancel_requested` contract. The
Turn becomes `CANCELED` only after runtime confirmation. If execution wins the
race, its success/partial output is preserved and the summary records
`CANCELLATION_REQUESTED_AFTER_EXECUTION_COMPLETED`.

No Phase 4 component selects Tools, changes parameters, reruns planning,
executes adapters directly, calls an LLM, interprets Artifacts, or creates a
ScientificResult.
