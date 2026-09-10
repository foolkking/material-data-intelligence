# Workstream F — Scientific Research Strategy & Advanced Reasoning

Status: ACTIVE IMPLEMENTATION AUTHORITY
Authorized: 2026-09-10
Canonical repository: `E:\1project\mdi-b0-5a1`

## Mission

Workstreams A–E are complete. Build a bounded, evidence-driven scientific
research strategy layer on top of the existing durable autonomy lifecycle.
The Agent must improve how it identifies unresolved scientific questions,
missing evidence, valuable next analyses, cross-family relationships,
testable hypotheses, contradictions, evidence sufficiency and scientifically
correct stop conditions.

The old repository `E:\1project\Material Data Intelligence` is
historical/comparison-only and must not be used for development or runtime.

## 1. Preserve the autonomy foundation

Autonomy remains explicitly activated, finite, durable, recoverable,
quality-aware, source-grounded and user-controllable. Keep the Workstream E
starting limits:

```text
max cycles = 4
max capability executions = 8
max dependency steps per cycle = 4
max LLM decisions = 8
context budget = 12,000 tokens
```

Do not increase limits to pass strategy tests. Improve decisions within the
same envelope.

## 2. Strategy authority boundary

Strategy may determine:

- the unresolved scientific question;
- what evidence would address it;
- whether a hypothesis is justified and testable;
- which qualified scientific need is most valuable;
- whether to continue, reuse, clarify, synthesize or stop.

Strategy may not execute code, invent Tools, bypass Capability eligibility,
qualification, authorization, exact identities, parameter validation or
execution policy. Execution remains:

```text
validated Capability → Tool → Adapter → Job → Artifact → ScientificResult
```

## 3. Strategy is not another planner

Reuse AnalysisIntent, Capability resolution, CapabilityPlan/AnalysisPlan and
bounded autonomy. The new semantic layer is:

```text
Research objective
→ evidence state
→ scientific question / evidence gap
→ research strategy decision
→ existing Capability planning
```

Strategy decides what evidence is worth seeking; the existing planner decides
how an eligible Capability obtains it.

## 4. Bounded reconnaissance

Inspect only current autonomy assessment, AnalysisIntent, Capability
selection, Result-driven continuation, ScientificResult facts/evidence,
Interpretation, Memory, ContextSnapshot, qualification metadata, dependency
chains, recommendation objects, Turn lineage, stop outcomes and synthesis.

Classify current hard-coded rules as:

```text
scientific invariant
capability-specific policy
temporary golden-case heuristic
general reusable research-strategy concept
```

Do not blindly generalize heuristics.

## 5. Evidence-state projection

Create or strengthen a read-only derived `ResearchEvidenceState` containing:

```text
objective
bounded subquestions
available ScientificResults
important observations
comparisons
limitations
contradictions
supported / unsupported conclusions
unresolved evidence gaps
exact source/version refs
qualification context
evidence lineage
```

ScientificResult remains authority. Evidence state is a strategy projection,
not a second truth store.

## 6. Scientific questions and gaps

Support bounded, goal-linked, source-aware subquestion decomposition. Use a
small question vocabulary such as:

```text
CHARACTERIZE
COMPARE
QUANTIFY
VALIDATE
EXPLAIN
TEST_HYPOTHESIS
CHECK_CONSISTENCY
IDENTIFY_LIMITATION
```

Use typed evidence gaps such as:

```text
PROPERTY_NOT_QUANTIFIED
COMPARISON_MISSING
STRUCTURAL_CONTEXT_MISSING
TRANSPORT_METRIC_MISSING
MODEL_ERROR_PATTERN_UNEXPLAINED
CONTRADICTORY_RESULTS
SOURCE_LIMITATION
METHOD_LIMITATION
```

An evidence gap describes missing evidence, not a Tool ID. Cap the number of
active subquestions.

## 7. Existing evidence first

Before new execution, check:

```text
current authoritative ScientificResult
→ compatible Result on current branch/project
→ new scientific execution
```

Preserve `REDUNDANT_EXECUTIONS = 0`.

## 8. Evidence value and minimum sufficiency

Compare candidate analyses using inspectable ordinal dimensions:

```text
relevance
ability to discriminate alternatives
qualification strength
applicability
novel evidence contribution
assumption dependence
cost/resource class
existing evidence overlap
```

Use `HIGH | MEDIUM | LOW` rather than fake probabilities.

Define minimum-sufficient-evidence rules where justified. For example,
trajectory + valid MSD + valid diffusion fit can satisfy a diffusion estimate
without unrelated RDF/XRD/ML. Open-ended explanation may remain uncertain.

## 9. Cross-family strategy

Support justified transitions such as:

```text
trajectory → structure
dataset → ML
ML → composition
structure → diffraction
structure → electronic
phonon → structure
```

Transitions must follow objective + current evidence + unresolved question,
not a static “always run next family” matrix.

Reusable example:

```text
transport anomaly established
+ objective asks for structural explanation
+ exact structure source available
→ structural characterization may be relevant
```

## 10. Hypothesis model and testing

If existing contracts are insufficient, add a bounded structured hypothesis:

```text
statement
research question
supporting evidence refs
contradicting evidence refs
epistemic status
testable predictions
known assumptions
```

It is not ScientificResult, fact or qualification evidence.

Allow hypotheses only for a real unresolved question, motivated by evidence
and scientifically testable/useful. Preserve states such as:

```text
PROPOSED
PARTIALLY_SUPPORTED
SUPPORTED_WITHIN_SCOPE
CONTRADICTED
UNRESOLVED
NOT_TESTABLE_WITH_AVAILABLE_CAPABILITIES
```

Translate a hypothesis into evidence requirements before Capability
selection. Prefer discriminating analyses over repeated general metrics.

## 11. Contradictions, comparisons and lineage

Classify apparent contradictions by:

```text
exact version
method
parameter convention
applicability domain
unit
statistical variation
genuine unresolved disagreement
```

Resolve deterministic semantic differences, such as eV/atom versus eV/cell,
when authority permits. Do not silently choose the latest Result.

Comparison requires compatible quantity semantics, units, method,
normalization, source type and conditions. `COMPARISON_NOT_VALID` is a valid
outcome.

Use provenance to avoid double-counting Result → Interpretation → Report as
independent evidence. Derived Results may be distinct quantities without being
independent sources.

## 12. Uncertainty and claim strength

Use uncertainty already present in Results, limitations, data coverage,
qualification, sample size and metrics. Do not invent probabilities.

Strategy/synthesis should distinguish:

```text
well-supported
qualified or method-dependent
limited evidence
conflicting evidence
insufficient evidence
```

Wording such as “shows”, “is consistent with”, “suggests”, “does not support”
and “cannot distinguish” must match evidence strength.

## 13. Strategy decision contract

Create or strengthen one bounded structured decision:

```text
ResearchStrategyDecision

objective
current question
evidence status
decision:
  SYNTHESIZE
  CONTINUE_ANALYSIS
  REUSE_RESULT
  TEST_HYPOTHESIS
  COMPARE
  NEEDS_CLARIFICATION
  STOP_WITH_LIMITATIONS
evidence gap
candidate capability need
selected evidence refs
hypothesis ref
limitation refs
decision provenance
```

No hidden reasoning.

## 14. Provider role and validation

The LLM may propose bounded structured question decomposition, gap
interpretation, hypothesis or cross-family scientific need. It cannot execute
or choose arbitrary Tool code.

Validate provider proposals independently:

- Result/source refs exist and belong to the Project;
- question remains tied to the user objective;
- hypotheses are not facts;
- evidence-gap type and need are known;
- Capability need is supported and qualification policy passes;
- budget remains;
- no duplicate semantic step or scope expansion.

Allow at most one validation-guided repair if current structured-provider
architecture supports it. Repair cannot expand scope, sources, Capability
universe or budget.

Strong deterministic scientific relations remain deterministic. Keep
Interpretation (“what Result means”) separate from Strategy (“what evidence to
seek next”).

## 15. Strategy memory and context

Persist only useful branch-scoped continuity:

```text
open question
active hypothesis/status
evidence gap
analysis rejected as irrelevant
important strategy decision
```

Do not duplicate operational events.

Each strategy decision receives a bounded ContextSnapshot with original
objective, current subquestion, relevant Results/Interpretations, hypotheses,
gaps, qualification, limitations and recent decisions. Do not include full
conversation history or the full Capability Registry.

Strategy reasons Result-first. Interpretation can organize meaning; Report and
Workspace never become scientific authority.

## 16. Family strategy expectations

### Dataset / ML

For model-performance/chemistry questions, inspect ML evaluation, identify the
specific missing pattern evidence, then request composition/material grouping
only when justified. Do not run every Dataset/ML Capability.

### Trajectory

Use MSD → diffusion for transport quantification. Add structure/RDF only when
the objective asks for explanation and evidence/source availability justifies
it.

### Structure

“Unusual” requires a comparison/reference basis. Without one, stop with
limitations or ask a specific clarification.

### Diffraction

Use experimental pattern + theoretical XRD + comparison where applicable,
while preserving broadening, phase-purity, peak-matching and measurement
limitations. Visual similarity is not phase confirmation.

### Electronic / phonon

`EXTERNAL_IMPLEMENTATION_SEMANTICS_VALIDATED` permits bounded analysis of
supplied outputs. It does not authorize claiming an independently validated
first-principles calculation.

## 17. Multi-source and comparative research

Track exact comparison identities such as Material A/V2 and Material B/V5.
Allow authorized Dataset, ScientificObject and prior Result evidence to be
combined without crossing Project boundaries.

Recommendations for unavailable analyses remain future recommendations, not
executable plans or fabricated evidence.

## 18. Stop and clarification quality

Improve `GOAL_SATISFIED` by recording resolved subquestions and supporting
evidence. Optional available analyses do not justify continuation.

Stop successfully when the conclusion cannot be established because of no
baseline, no qualified Capability, unavailable external result, insufficient
sample, method limitation, conflict or unsupported causality.

Clarify only when a specific user choice is necessary, based on real
authorized candidates.

## 19. Scientific synthesis

Organize final synthesis by:

```text
Question
Evidence
Finding
Alternative explanations
Limitations
Remaining uncertainty
Suggested future research
```

Execution chronology remains in provenance/timeline. Do not create facts at
synthesis time.

## 20. Strategy UI and observability

Expose only concise observable strategy state:

```text
current question/subgoal
active hypothesis
next analysis and evidence rationale
resolved/unresolved questions
why research continued/stopped
```

Optionally expose a compact durable research map. Do not expose prompts,
candidate-scoring internals or chain-of-thought. Do not redesign Research UI.

## 21. Strategy evaluation corpus

Create 12–20 high-quality deterministic cases spanning:

- single-family;
- cross-family;
- comparison;
- hypothesis testing;
- insufficient evidence;
- contradictory evidence;
- reuse-heavy;
- irrelevant-Capability traps.

Required representative cases:

```text
A trajectory transport
B trajectory transport + structural explanation
C ML error + chemistry pattern
D structure comparison needing a reference
E experimental/theoretical diffraction comparison
F electronic supplied-result interpretation under external-semantics limits
G conflicting Results
H existing Results already sufficient
I irrelevant high-quality Capability trap
J scientifically unanswerable causal claim
```

Evaluate required/acceptable evidence, forbidden irrelevant analyses, required
limitations and valid stops rather than overfitting one exact Tool sequence.

Metrics:

```text
EVIDENCE_GAP_IDENTIFICATION_ACCURACY
QUALIFIED_ANALYSIS_SELECTION_RATE
IRRELEVANT_ANALYSIS_RATE
REDUNDANT_EXECUTION_RATE
CORRECT_CROSS_FAMILY_TRANSITION_RATE
CORRECT_STOP_RATE
HYPOTHESIS_GROUNDING_RATE
HYPOTHESIS_OVERCLAIM_RATE
CONTRADICTION_HANDLING_RATE
COMPARISON_COMPATIBILITY_RATE
LIMITATION_PRESERVATION_RATE
MINIMUM_SUFFICIENT_EVIDENCE_RATE
IRRELEVANT_CAPABILITY_EXECUTIONS
```

Small-corpus rates are regression signals, not population statistics.

## 22. Real provider and service verification

Default CI remains deterministic. Run several sanitized qualification-owned
real-provider strategy cases across families when configuration is available.
Record objective, ContextSnapshot, structured outcome, evidence gap, selected
Capability need, sequence, stop, Result refs and provider call count without
hidden reasoning or secrets.

Test invalid provider proposals: invented Result, irrelevant Capability,
invalid qualification, unsupported hypothesis, cross-project source, duplicate
analysis and scope expansion.

Use canonical PostgreSQL, Redis/RQ, MinIO, fresh workers, API and frontend where
useful. Verify:

```text
one cross-family Result-driven case
one comparison case
one hypothesis-testing case
one existing-evidence/no-new-execution case
one insufficient-evidence stop
one contradiction/limitation case
```

Do not repeat full release qualification.

## 23. Regression requirements

Do not degrade:

```text
REDUNDANT_EXECUTIONS = 0
QUALIFIED_CAPABILITY_SELECTION_VIOLATIONS = 0
UNSUPPORTED_CLAIM_VIOLATIONS = 0
bounded autonomy
exact source identity
recovery/cancellation
ContextSnapshot provenance
quality qualification enforcement
```

## 24. Persistence and implementation boundaries

Use current Turn decisions, Memory and events before adding persistence.
Potential concepts are ResearchQuestion, EvidenceGap, ScientificHypothesis and
ResearchStrategyDecision, but do not create four tables merely because four
concepts exist. Persist only what needs durable identity/recovery; derived
evidence state remains derived.

Avoid a strategy God object. Prefer cohesive evidence projection, question/gap,
hypothesis, proposal, validation, comparison and evaluation responsibilities.
Do not add a graph database, generic RAG/vector store, unbounded literature
research, generic multi-agent system or unavailable experimental execution.

## 25. Documentation

Create/update:

```text
docs/agent2/strategy/SCIENTIFIC_RESEARCH_STRATEGY.md
docs/agent2/strategy/HYPOTHESIS_AND_EVIDENCE_POLICY.md
docs/agent2/strategy/generated/strategy_evaluation.json
PROJECT_STATE.md
results.md
persistent/DESIGN_PROGRESS.md
persistent/TASK_BOARD.md
```

Update shared schema and ADR/changelog when actual contracts or decisions
change. Do not create another broad architecture review.

## 26. Completion criteria

Evidence must support:

```text
SCIENTIFIC_STRATEGY_MODEL = COHERENT
RESEARCH_QUESTION_MODEL = PASS
EVIDENCE_STATE_PROJECTION = PASS
EVIDENCE_GAP_MODEL = PASS
EXISTING_EVIDENCE_FIRST = PASS
CROSS_FAMILY_STRATEGY = PASS
HYPOTHESIS_MODEL = PASS
HYPOTHESIS_IS_NON_AUTHORITY = ENFORCED
HYPOTHESIS_TESTING = PASS
EVIDENCE_LINEAGE_AWARENESS = PASS
COMPARISON_COMPATIBILITY = PASS
CONTRADICTION_HANDLING = PASS
QUALIFICATION_AWARE_STRATEGY = PASS
STRATEGY_DECISION_VALIDATION = PASS
MINIMUM_SUFFICIENT_EVIDENCE_POLICY = PASS
IRRELEVANT_ANALYSIS_PREVENTION = PASS
GOAL_SATISFACTION_REASONING = PASS
INSUFFICIENT_EVIDENCE_STOP = PASS
SCIENTIFIC_SYNTHESIS = PASS
STRATEGY_CONTEXT_PROVENANCE = PASS
STRATEGY_RECOVERY = PASS
REAL_SERVICE_CROSS_FAMILY_RESEARCH = PASS
REAL_PROVIDER_STRATEGY_EVALUATION = PASS
SCIENTIFIC_STRATEGY_EVALUATION_SUITE = PASS
```

Report:

```text
STRATEGY_EVALUATION_CASES
REAL_LLM_STRATEGY_CASES
CROSS_FAMILY_CASES
HYPOTHESIS_TEST_CASES
CONTRADICTION_CASES
IRRELEVANT_CAPABILITY_EXECUTIONS
REDUNDANT_EXECUTIONS
CORRECT_SCIENTIFIC_STOPS
CORRECT_CROSS_FAMILY_TRANSITIONS
HYPOTHESIS_OVERCLAIM_VIOLATIONS
COMPARISON_COMPATIBILITY_VIOLATIONS
QUALIFICATION_POLICY_VIOLATIONS
UNSUPPORTED_CLAIM_VIOLATIONS
UNRESOLVED_STRATEGY_BLOCKERS
```

## 27. Final assessment

Answer directly whether the Agent can:

1. decompose broad goals into useful subquestions;
2. identify missing evidence;
3. avoid capability-driven busywork;
4. move across families when justified;
5. refuse irrelevant cross-family analysis;
6. formulate bounded hypotheses;
7. distinguish hypothesis from evidence;
8. choose analyses that test hypotheses;
9. distinguish dependent/independent evidence;
10. compare only semantically compatible Results;
11. preserve unresolved contradiction;
12. recognize sufficient existing evidence;
13. stop when more analysis has low value;
14. stop when conclusions are impossible;
15. preserve qualification/method limitations;
16. synthesize coherently across Results;
17. improve real-provider strategy beyond Workstream E heuristics;
18. identify remaining family-specific strategy;
19. identify the dominant remaining bottleneck;
20. support broader scientist-facing autonomous research.

Set:

```text
SCIENTIFIC_AGENT_STRATEGY_MATURITY =
  CROSS_FAMILY_READY | BOUNDED_READY | PARTIAL | NOT_READY
```

Select the next workstream from actual evidence:

```text
Long-Running Research, Scale & Fault Tolerance
Scientist UX & Product Maturity
Scientific Knowledge & Literature Integration
Advanced Scientific Capability Expansion
```

## 28. Working rules

- Work autonomously in the canonical repository only.
- Do not restart A–E, migration or release qualification.
- Do not push.
- Do not increase autonomy bounds.
- Do not create unrestricted reasoning loops or generic agent frameworks.
- Do not execute analyses merely because a Tool exists.
- Do not promote hypotheses to facts or plausibility to evidence.
- Prefer question → gap → minimum evidence → justified qualified analysis →
  Result → reassess → scientifically correct stop.
