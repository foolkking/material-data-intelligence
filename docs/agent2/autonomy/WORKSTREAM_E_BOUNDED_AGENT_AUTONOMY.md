# Workstream E — Bounded Agent Autonomy & Multi-Step Scientific Research

Status: AUTHORIZED / IN PROGRESS

Canonical repository:

```text
E:\1project\mdi-b0-5a1
```

The old `E:\1project\Material Data Intelligence` tree is historical and must
not be used for active development, testing, or runtime.

This file is the repository execution authority for the user-authorized
Workstream E prompt. It preserves the complete implementation obligations
below; it is not a replacement architecture review or release gate.

## Mission and invariant

Extend the existing Research Agent so one explicitly autonomous research
objective can perform more than one scientifically justified analysis cycle,
observe durable ScientificResults, choose a qualified eligible next
Capability, reuse existing Results, and stop when sufficient or unable to
progress safely.

The Agent remains durable, finite, recoverable, quality-aware,
source-grounded, provenance-preserving and user-controllable. The LLM is only a
bounded structured decision component. Authorization, eligibility,
qualification lookup, budget enforcement, Tool/Adapter binding, execution,
ScientificResult and grounding remain deterministic authorities.

Do not introduce another Agent framework, workflow engine, Job model, memory
store, Tool registry, arbitrary-code/shell authority, or latest-wins source
identity. Preserve A-D authorities, queue/handler/Tool/Adapter identities,
public contracts and exact ScientificObjectVersion/Result/Artifact identity.

## Canonical autonomous cycle

```text
User goal
→ ResearchTurn
→ ContextSnapshot
→ AnalysisIntent / Requirements
→ eligible and quality-appropriate Capabilities
→ CapabilityPlan / AnalysisPlan
→ Job / ToolCall / Artifact
→ ScientificResult
→ grounded Interpretation
→ durable ResearchProgressAssessment
→ stop, reuse, clarify, or start the next bounded cycle
```

Each meaningful cycle must cross durable Workstream A authorities. Replanning
must consume persisted Artifact/ScientificResult/Interpretation evidence, not
unpersisted Tool output. Every cycle receives a new bounded Workstream B
ContextSnapshot containing the original objective, current subgoal, exact
sources, relevant Results/Memory and bounded qualification metadata.

## Activation and policy

Preserve ordinary single-analysis behavior. Autonomy must be explicitly
activated through a bounded product/API contract (`STANDARD` versus
`BOUNDED_AUTONOMOUS`, or the closest current vocabulary); generic words such
as “analyze” must not silently enable it.

Use one versioned/fingerprinted policy owner for:

```text
maximum cycles
maximum total capability executions
maximum dependency steps
maximum LLM decision calls
maximum retries/replans
maximum context budget
maximum execution/cost class
allowed qualification classes
```

The policy caps are authoritative even if the LLM proposes continuation.
Autonomous research must always have a deterministic finite stop path.
Historical decisions retain the policy identity under which they ran.

## Scientific qualification policy

Eligibility, qualification and planning remain separate.

- `DOMAIN_VALIDATED`: autonomous use is allowed only inside declared
  applicability and when it materially contributes to the current objective.
- `REFERENCE_VALIDATED`: autonomous use is allowed inside validated
  assumptions while retaining known limitations.
- `EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED`: bounded use is allowed for the
  platform-owned parsing/library/projection semantics actually validated, but
  downstream interpretation and synthesis must retain that the upstream
  solver/library was not independently validated.
- structural-only, stale, not-qualified, disabled or experimental capability
  must not be autonomously selected by default.

Consume the current Workstream D evidence fingerprint. Stale qualification is
not current qualification. Planner context may receive only bounded level,
applicability, critical limitations and scientific-contract fingerprint.

## Progress assessment and decision provenance

After a durable Result and grounded Interpretation, create or reuse the
smallest existing durable decision/event authority capable of representing a
structured progress assessment. Do not store chain-of-thought.

Supported outcomes must cover the semantics:

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

Persist bounded observable fields such as objective coverage, unresolved
requirement, evidence/result refs, eligible capabilities, selected capability,
qualification/fingerprint, critical limitation, cycle/attempt, policy
identity, budget consumption and typed stop/continue reason. This projection
must explain why the Agent continued or stopped without exposing hidden model
reasoning.

## Reuse, duplicate and loop prevention

Before execution, resolve whether an authorized ScientificResult already
satisfies the required evidence using exact:

```text
Capability
ScientificObjectVersion refs
meaningful parameters/method
Result fingerprint
research branch/objective
```

Reuse it when valid and create zero redundant ToolCalls. Record meaningful
parameter/source changes when repetition is justified.

Persist/derive semantic step signatures to prevent identical analysis,
repeated reinterpretation, A→B→A loops, repeated unsupported requirements and
clarification loops. Stop with a typed `NON_PROGRESS` outcome rather than
creating another Job.

## Stop, contradiction and epistemic behavior

Mandatory stops include objective satisfied, no qualified next capability,
clarification required, policy budget exhausted, non-progress, unresolved
conflicting evidence, cancellation and unsupported inference.

Contradictory Results must retain source versions, methods, assumptions,
units, applicability and tolerance. Do not use last-result-wins. A further
qualified analysis may be selected only when it can materially discriminate;
otherwise stop/clarify with limitations.

Research Memory preserves user/Agent hypothesis, computed observation,
interpretation, constraint and decision epistemic categories. Hypotheses may
motivate analysis but are not evidence. Write only useful durable scientific
continuity after meaningful cycles.

## Dependency plans and result-driven continuation

Keep the distinction between:

- known dependency composition, such as `trajectory.msd →
  trajectory.diffusion`;
- result-driven next-cycle selection that is justified only after observing a
  new ScientificResult.

Do not build an arbitrary DAG product or precompute an unbounded mega-plan.
Use existing CapabilityPlan/AnalysisPlan and Artifact-port contracts.

Golden families/scenarios:

1. trajectory transport: exact trajectory → MSD → diffusion → synthesis;
2. dataset/model diagnosis: ML evaluation, then only justified
   materials/composition analysis;
3. bounded structure characterization using reference/domain-supported
   capabilities;
4. diffraction comparison where applicability permits;
5. insufficient evidence stops with limitations;
6. electronic/phonon participation retains external-semantics limits;
7. existing Result reuse creates no redundant ToolCall;
8. cancellation after completed science preserves Result and blocks future
   cycles;
9. failure between cycles recovers from persisted Result/assessment;
10. repeated next-step proposal stops as non-progress.

## Lifecycle, recovery and cancellation

Integrate with Workstream A:

```text
Tool failure → recover the Tool stage when permitted
Result exists / interpretation fails → retry interpretation only
Result + interpretation exist / assessment fails → retry assessment only
next Job publication fails → recover the existing Job
```

Autonomy must be reconstructible after process restart. A stale worker may not
overwrite a newer cycle owner. Cancellation stops future cycles and unnecessary
queued work while preserving completed Artifacts, Results, Interpretations and
provenance. Pause/resume is optional only if naturally supported.

## Synthesis, Report and UI

Final synthesis is a bounded grounded projection over selected
ScientificResults, Interpretations, methods, limitations, contradictions and
qualification context. It creates no new scientific facts and distinguishes
computed evidence, interpretation, inference, uncertainty and untested scope.

Reports may communicate the objective, analyses, exact source versions,
methods, Results, findings, limitations and unresolved questions, but are not
scientific input authority.

Make only bounded Research UI changes needed to show autonomy mode, cycle,
scientific step, evidence used, why the next capability was selected, why work
stopped, Stop/manual-continue/source actions and provenance. Do not expose raw
prompts, chain-of-thought, worker details or large JSON.

Extend the existing read-only lifecycle/correlation projection with autonomy
enabled, cycle, policy, objective/subgoal, Results, qualification, decision,
next capability, stop reason and budget consumption. Do not create another
lifecycle authority.

## Evaluation and tests

Focused tests must cover:

```text
explicit activation
cycle/tool/decision caps
quality/applicability/staleness policy
result-driven continuation
reuse before recompute
duplicate and loop prevention
goal/no-qualified/clarification/budget stops
external-semantics limitation propagation
ContextSnapshot per cycle
Memory epistemic preservation
cross-project rejection
cancellation and stale-owner protection
recovery from durable Result
grounded final synthesis
```

Create a bounded machine-readable autonomy evaluation corpus/report containing
goal, required evidence, allowed/forbidden capability families, minimum/
maximum useful work, actual sequence, Result refs, qualification, stop reason
and violations. Avoid rigid exact paths when several scientific paths are
valid. Measure qualified selection, inapplicable/redundant execution,
reuse, correct stop, unnecessary continuation, limitation preservation,
unsupported claims and cross-project violations.

Test deterministic/fake-provider behavior and, when safe approved provider
configuration exists, a sanitized real-provider case. Never store secrets or
hidden reasoning.

## Real-service verification

Use canonical PostgreSQL, Redis/RQ, MinIO, fresh workers and API with
qualification-owned data. Verify at least:

```text
one dependency-aware multi-step case
one result-driven continuation case
one Result-reuse case
one cancellation/recovery case
one limitation/stop case
```

Do not run release qualification or use old-tree processes.

## Completion gates

```text
AUTONOMY_CONTROL_MODEL = COHERENT
BOUNDED_AUTONOMY_POLICY = PASS
AUTONOMY_IS_EXPLICITLY_ACTIVATED = PASS
AUTONOMOUS_CYCLE_IS_DURABLE = PASS
QUALITY_AWARE_CAPABILITY_SELECTION = PASS
QUALIFICATION_APPLICABILITY_ENFORCEMENT = PASS
EXTERNAL_SEMANTICS_LIMITATION_PROPAGATION = PASS
RESULT_DRIVEN_REPLANNING = PASS
REUSE_BEFORE_RECOMPUTE = PASS
DUPLICATE_ANALYSIS_PREVENTION = PASS
NON_PROGRESS_LOOP_PREVENTION = PASS
GOAL_SATISFACTION_STOP = PASS
NO_QUALIFIED_CAPABILITY_STOP = PASS
CLARIFICATION_STOP = PASS
BUDGET_ENFORCEMENT = PASS
CANCELLATION_PRESERVES_RESULTS = PASS
RECOVERY_FROM_LATEST_DURABLE_CYCLE = PASS
CONTEXT_SNAPSHOT_PER_CYCLE = PASS
SCIENTIFIC_MEMORY_CONTINUITY = PASS
AUTONOMY_DECISION_PROVENANCE = PASS
NO_HIDDEN_REASONING_EXPOSURE = PASS
FINAL_SYNTHESIS_GROUNDING = PASS
REAL_SERVICE_MULTI_STEP_RESEARCH = PASS
REAL_SERVICE_RESULT_DRIVEN_CONTINUATION = PASS
AUTONOMY_EVALUATION_SUITE = PASS
```

Final reporting must include maturity (`BOUNDED_READY | PARTIAL | NOT_READY`),
golden/real-LLM case counts, qualification violations, redundant executions,
loop-prevention events, correct scientific stops, unsupported-claim
violations, unresolved blockers, direct answers to the requested fifteen
scientific assessment questions, and an evidence-based recommendation for
Workstream F.

Do not push, perform remote CI, reopen A-D/migration, create unlimited loops,
add generic agent frameworks, or weaken scientific criteria.
