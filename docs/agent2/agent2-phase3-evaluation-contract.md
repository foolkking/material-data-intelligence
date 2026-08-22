# Agent 2.0 Phase 3 Evaluation Contract

The deterministic suite covers PLAN_READY semantics, RDF fast-path planning,
real XRD and trajectory artifact-port dependencies, phonon alternative
planning, unsupported/wrong-type requests, explicit cutoff preservation,
unknown capability and omitted-requirement rejection, cycle rejection, Tool
version failure, bounded LLM repair outside transactions, processor
idempotency, exact Result-output reuse, exact plan attachment, and the
no-execution invariant.

The local suite names and asserts every P3-C01 through P3-C20 boundary,
including ML exact-version input, invalid output ports, recomputation and stale
Result non-reuse, Existing PlanValidator rejection, concurrent service-backed
claiming and zero execution-object deltas.

Successful cases require one AnalysisPlan and zero Job, ToolCall and Artifact
rows. Existing Phase 1/2 tests remain independent authorities. Live DeepSeek
planning is gated by `MDI_RUN_AGENT2_LIVE=1` and `DEEPSEEK_KEY`; ordinary CI
does not consume provider credits. The live gate covers a genuinely ambiguous
phonon strategy; single-path RDF, XRD producer chains, trajectory planning and
Result reuse remain deterministic and make zero planner-provider calls.
