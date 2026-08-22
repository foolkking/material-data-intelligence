# Agent 2.0 Phase 4 Evaluation Contract

Phase 4 qualification is deterministic and has no live-LLM dependency.

The focused suite covers idempotent and concurrent dispatch, queue-publish
recovery with the same Job, real start/terminal synchronization, exact-version
hydration, tamper and cross-Project rejection, incremental output event
ordering, partial/full failure classification, cancellation confirmation and
race preservation, summary conflict protection, product DTO redaction, SSE
resume, and frontend queued/running/canceling/partial/result-pending states.

The service-backed gate upgrades a fresh PostgreSQL database through `0020`,
stores exact structure and experimental-XRD payloads in MinIO, creates Turns
through the Phase 2/3 deterministic boundaries, publishes only each `job_id`
to Redis/RQ, and executes them in fresh Python Worker processes. It verifies
one Job per Turn, real ToolCalls/Artifacts, SUCCESS ExecutionSummaries, zero
ScientificResultSnapshots, and no assistant final message.

RDF and the two-step theoretical/experimental XRD DAG are real Agent 2.0
end-to-end execution qualifications. The XRD Worker is held by a test-only
barrier after its committed step-1 output notification so the parent process
can prove the Artifact is visible while the Job is still non-terminal.
Trajectory, phonon, partial execution and other dependency semantics retain
their existing real runtime service tests; Phase 4 does not claim all five
families were newly executed end to end.
