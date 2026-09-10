# Scientific Research Strategy

Status: implemented bounded strategy layer
Canonical repository: `E:\1project\mdi-b0-5a1`
Contracts: `agent2.research-evidence-state/1.0`,
`agent2.research-strategy-decision/1.0`

## Boundary

Workstream F adds a strategy projection above bounded autonomy. It answers
**what evidence is worth seeking next**. It does not replace
`AnalysisIntent`, Capability Resolution, Capability Plan, Tool Registry,
execution, ScientificResult or Interpretation.

```text
Research objective
→ ResearchEvidenceState (derived)
→ ResearchStrategyDecision (structured)
→ Capability requirement
→ existing eligibility/qualification/planning
→ Tool / Adapter / Result
```

No strategy output can execute code, invent a capability, bypass authorization,
change an exact source version, or bypass the Workstream E policy.

## Evidence state

`ResearchEvidenceState` is a bounded, read-only projection over authoritative
`ScientificResultBundle` values. It records exact Result and
ScientificObjectVersion references, typed observations with units and lineage,
bounded questions and evidence gaps, contradictions, comparison compatibility,
limitations and evidence strength.

`ScientificResult` remains the scientific knowledge authority. Interpretation,
Report, Workspace and Memory are not promoted by this projection.

## Strategy vocabulary

Questions are typed as `CHARACTERIZE`, `COMPARE`, `QUANTIFY`, `VALIDATE`,
`EXPLAIN`, `TEST_HYPOTHESIS`, `CHECK_CONSISTENCY` or
`IDENTIFY_LIMITATION`. Evidence gaps describe missing evidence rather than
Tool IDs, for example `TRANSPORT_METRIC_MISSING`,
`STRUCTURAL_CONTEXT_MISSING`, `COMPARISON_MISSING`,
`MODEL_ERROR_PATTERN_UNEXPLAINED` and `REFERENCE_BASELINE_MISSING`.

Decisions are one of `SYNTHESIZE`, `CONTINUE_ANALYSIS`, `REUSE_RESULT`,
`TEST_HYPOTHESIS`, `COMPARE`, `NEEDS_CLARIFICATION`,
`CONFLICTING_EVIDENCE` or `STOP_WITH_LIMITATIONS`.

## Existing evidence first

The engine checks current Results and completed capabilities before proposing
new work. Minimum-sufficient paths are explicit for the strongest current
families:

- transport: MSD, then diffusion fitted only from persisted MSD facts;
- transport explanation: optional trajectory RDF only when the objective asks
  for explanatory structural context;
- dataset/model: model evaluation before composition-pattern comparison;
- local structure: RDF before coordination distribution;
- diffraction comparison: theoretical pattern, experimental reference, then
  comparison;
- electronic: supplied-result inspection only; no solver is invented.

An available Capability is not itself evidence that it should run.

## Cross-family and hypothesis behavior

Cross-family transitions are objective and evidence driven. A strategy can
move from ML evaluation to composition space or from transport to structural
context when the evidence gap requires it. It does not execute a family-wide
sweep.

Hypotheses are bounded strategy objects. They carry supporting/contradicting
Result references, predictions and assumptions. They remain `PROPOSED`,
`PARTIALLY_SUPPORTED` or `UNRESOLVED` until evidence changes their status.
They are never inserted into ScientificResult facts or treated as execution
authority. Causal requests stop with a limitation unless actual causal
evidence exists.

## Contradiction and comparison

The projection compares matching predicates and checks unit dimensions,
method/source lineage and exact source versions. Known incompatibility is
classified rather than silently merged. Genuine unresolved disagreement
remains visible as `CONFLICTING_EVIDENCE`; the latest Result does not
automatically win.

## Provider boundary

`BoundedStrategyProvider` accepts only a bounded structured proposal. It
validates all question, evidence-gap, hypothesis and Result references,
requirement IDs and duplicate-step constraints. One validation-guided repair
is allowed. Invalid output after that boundary is rejected. The provider
never decides authorization, eligibility, qualification, parameters or
execution.

## Lifecycle and observability

The existing `AutonomyAssessment` carries the strategy decision and compact
summary. The existing lifecycle projection exposes action, evidence-state
fingerprint/strength, question/gap/hypothesis counts and active bounded
objects without prompts or hidden reasoning. Existing Turn events remain the
durable authority and child Turns continue to use Workstream E idempotency,
recovery, cancellation and policy limits.

The ordinary Research progress API includes this bounded projection only for
explicitly autonomous Turns. The Research activity surface shows the current
scientific question, missing evidence, tentative hypothesis, continuation
basis or typed stop reason, and the first critical limitation. It does not
expose prompts, free-form model reasoning, worker identities or raw
Tool/Adapter identifiers.

## Evaluation

Run:

```text
PYTHONPATH=apps/api;packages/schemas;packages/tool-registry
python scripts/scientific_strategy_evaluation.py --check
```

The deterministic corpus contains 12 accepted cases covering transport,
cross-family dataset/ML, diffraction comparison, structural baseline,
external-semantics electronic limits, causal refusal, partial results,
existing-evidence reuse and contradiction handling. It records 7/7 correct
scientific stops, 1/1 correct cross-family transition and zero irrelevant,
redundant, overclaim, comparison, qualification or unsupported-claim
violations. The generated report is
`docs/agent2/strategy/generated/strategy_evaluation.json`.

Three sanitized live DeepSeek strategy cases pass the same structured
validation boundary. Canonical service-backed verification also covers a
fresh-worker MSD → diffusion durable recovery/reuse path, a Result-driven ML
evaluation → composition-space cross-family decision and planning path using
an exact Dataset version, and an existing real composition-space capability
path. The canonical API runtime on port 8007 reported PostgreSQL, Redis,
MinIO, DeepSeek configuration and all six queue identities healthy.

## Known limitations

- The engine is intentionally bounded to typed rules for the strongest
  platform families; it is not a general scientific strategy language.
- Live-provider strategy evaluation remains opt-in and is not a default CI
  dependency even though the bounded acceptance cases pass.
- Comparison compatibility is conservative and does not claim statistical
  independence or causal inference.
- No literature, internet or external scientific database authority is added.
- Indivisible ToolCalls still cannot resume inside a scientific algorithm.
