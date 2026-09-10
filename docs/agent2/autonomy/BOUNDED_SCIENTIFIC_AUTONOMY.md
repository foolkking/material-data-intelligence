# Bounded Scientific Autonomy

## Purpose

Workstream E extends the existing Research lifecycle with an explicitly
activated, finite multi-cycle mode:

```text
ResearchTurn
→ ContextSnapshot
→ CapabilityPlan / AnalysisPlan
→ Job / ToolCall / Artifact
→ ScientificResult
→ Interpretation
→ AutonomyAssessment
→ child ResearchTurn or typed stop
```

It does not create a second Agent, workflow engine, Result authority, memory
store, or Tool registry. Every continuation re-enters the canonical durable
ResearchTurn and queue-owned lifecycle.

## Activation and authority

`CreateResearchTurnRequest.autonomy_mode` is:

```text
STANDARD
BOUNDED_AUTONOMOUS
```

`STANDARD` remains the default. Autonomous continuation is never inferred from
ordinary wording alone.

The original user Turn owns the research objective and exact selected sources.
An autonomous child Turn stores a bounded generated subgoal, the parent Turn,
the Result used as evidence, exact ScientificObjectVersion identities, selected
Capability, parameters, qualification snapshot, policy identity and semantic
step signature. It cannot widen the original objective.

## Durable cycle boundary

Autonomy advances only after the current Turn has:

1. a terminal lifecycle state;
2. a durable ScientificResult;
3. a durable grounded Interpretation.

The progress assessment is persisted as a `ResearchTurnEvent`. A continuation
creates one idempotent child ResearchTurn and then publishes that existing
identity to the normal orchestration queue. If publication fails, recovery
republishes the same child rather than creating another Turn or Job.

Each child Turn builds its own bounded ContextSnapshot. Context, capability
resolution, planning, execution, projection and interpretation remain owned by
their existing stages.

## Progress outcomes

`AutonomyAssessment 1.0` supports:

```text
GOAL_SATISFIED
CONTINUE_WITH_ANALYSIS
REUSE_EXISTING_RESULT
NEEDS_CLARIFICATION
NO_QUALIFIED_CAPABILITY
CONFLICTING_EVIDENCE
BUDGET_EXHAUSTED
NON_PROGRESS
STOP_WITH_LIMITATIONS
CANCELLED
```

The assessment persists structured scientific decision provenance only:
evidence Result IDs, exact source versions, unresolved requirement, selected
Capability and parameters, qualification, limitations, reason codes and policy
identity. Prompts, scratchpads and hidden chain-of-thought are not persisted or
exposed.

## Reuse before recompute

The semantic step signature covers:

```text
Capability ID
exact ScientificObjectVersion IDs
meaningful parameters
```

An identical completed step on the current branch causes reuse or a typed
non-progress stop rather than another execution.

Direct cross-run Artifact reuse is narrowly allowed only when a registered Tool
input port declares `EXACT_PROJECT_DATASET_ARTIFACT`. The worker then validates
project, Dataset, Artifact kind, schema version, media type, size and checksum,
and materializes only inert JSON. Same-plan producer/consumer relationships
continue to use ordinary dependency bindings.

The initial reference path is:

```text
trajectory.msd Artifact
→ exact persisted reuse
→ trajectory.diffusion
```

The diffusion fit interval is taken from exact MSD ScientificResult facts. No
physical-time interval is guessed.

## Scientific memory

Each meaningful assessment writes at most one typed, idempotent Research Memory
item with:

```text
authority = MEMORY
epistemic status = DECISION
source Result refs
completed Capability refs
assessment provenance ref
```

Memory records continuity. ScientificResult remains the scientific evidence
authority.

## Cancellation and recovery

Cancellation prevents future autonomous publication and execution while
preserving already committed Artifacts, ScientificResults and Interpretations.

Recovery always starts from the latest durable boundary:

| Failure | Recovery boundary |
| --- | --- |
| assessment process restarts | reuse persisted assessment event |
| child creation repeats | return the child with the same assessment signature |
| queue publication fails | republish the existing child Turn |
| child execution fails | use the existing Workstream A stage-aware recovery |
| interpretation fails | retry interpretation; do not rerun completed science |
| cancellation | stop future cycles; retain completed evidence |

## Observability

The existing lifecycle projection now exposes a read-only `autonomy` section:

```text
enabled / mode
root Turn and cycle
policy version/fingerprint and caps
objective/subgoal
decision outcome and reason codes
selected Capability and parameters
evidence Result refs and exact source versions
qualification and limitations
child Turn / queue publication state
typed stop reason
```

This projection is not lifecycle authority.

## Current bounded strategy

The deterministic progress assessor is intentionally conservative. The golden
families currently covered are:

```text
trajectory.msd → trajectory.diffusion
ML/materials exploration → composition-space investigation
structure.rdf → coordination histogram
```

It also stops unsupported causal requests, partial Result continuation,
duplicate semantic steps and exhausted policy budgets. Initial intent selection
may use the configured structured LLM provider, but downstream authorization,
eligibility, qualification, parameters, execution and grounding remain
deterministic authorities.

## Known limits

- This is bounded autonomy, not an arbitrary research DAG or open-ended Agent.
- Cross-family scientific strategy remains intentionally shallow.
- A single indivisible ToolCall cannot be checkpointed beyond its real runtime
  capabilities.
- The real-provider acceptance case validates bounded ingress and initial
  capability selection; downstream golden continuation is deterministic.
- Large-scale, multi-hour and high-concurrency autonomous research is not
  proven by this workstream.

