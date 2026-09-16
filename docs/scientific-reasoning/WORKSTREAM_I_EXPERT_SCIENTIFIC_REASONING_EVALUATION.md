# Workstream I — Expert Scientific Reasoning Evaluation

Status: COMPLETE / LOCAL_EVIDENCE_VERIFIED  
Authorized: 2026-09-11  
Canonical repository: `E:\1project\mdi-b0-5a1`

## Mission

Work directly on the current uncommitted, locally validated Workstream H
baseline. Do not reset, clean, checkout, reconstruct, or discard it. The
historical repository is comparison/recovery-only.

Workstream I is evaluation-first. It must determine and improve whether claims
constructed from authoritative ScientificResults and LiteratureEvidence are
warranted at the scientific strength, scope, condition, and methodological
level in which they are stated.

The invariant remains:

```text
ScientificResult
!= LiteratureEvidence
!= Interpretation
!= Hypothesis
!= CapabilityQualification
```

No new scientific truth authority, workflow engine, literature provider,
generic web search, graph database, arbitrary execution authority, or
chain-of-thought persistence is authorized.

## Mandatory execution order

1. Inspect only current reasoning contracts and the H baseline.
2. Create a repository-owned, machine-readable expert-reasoning corpus that
   can fail the current system.
3. Run and preserve the immutable baseline before changing reasoning behavior.
4. Classify actual failures by scientific defect type and severity.
5. Implement the minimum reusable contracts, deterministic validators, and
   bounded provider behavior needed to fix defect patterns.
6. Rerun the same corpus, add regressions for discovered defect classes, and
   preserve before/after evidence.
7. Run focused A–H regression and representative real persisted/provider paths.
8. Update canonical project authorities and close the task honestly.

Do not implement a framework first and manufacture matching tests afterward.

## Operational definition

Expert scientific reasoning in this workstream means that the system can:

- distinguish direct observation, interpretation, association, mechanism,
  causality, generalization, limitation, and recommendation;
- calibrate wording to evidence strength without invented probabilities;
- preserve material, system, composition, phase, method, temperature,
  pressure, time/length scale, dataset population, task, and source-version
  scope when those dimensions are available;
- preserve method identity and classify method comparisons without a universal
  method-quality score;
- distinguish compatible, qualified, complementary, method-dependent,
  incomparable, and metadata-insufficient comparisons;
- preserve genuine contradiction and recognize condition/method explanations;
- avoid double-counting common-lineage Results, preprint/published versions,
  and review/primary-source relationships;
- reject unsupported causal and established-mechanism claims;
- preserve hypotheses as non-authoritative;
- distinguish evidence of absence from absence of evidence;
- avoid deriving numeric facts in the LLM; any needed arithmetic or conversion
  must use a narrow deterministic, provenance-preserving authority;
- stop at insufficient evidence when stronger inference is unwarranted.

## Additive claim/support model

Inspect and evolve existing `ScientificClaim`,
`GroundedScientificInterpretation`, `ResearchEvidenceState`,
`ResearchStrategyDecision`, `LiteratureEvidence`, and
`ScientificReportOutput` contracts. Prefer backward-readable additive changes.
Do not create a parallel interpretation or truth system.

A bounded derived assessment may include:

```text
claim
claim_type
support_status
supporting Result/Literature refs
contradicting refs
scope
method context
required qualifiers
claim-linked limitations
comparison status
reasoning contract/prompt/validator version
```

It may retain a compact observable support explanation but never hidden model
reasoning.

Claim types should remain small and include, where needed:

```text
DIRECT_OBSERVATION
DESCRIPTIVE_SYNTHESIS
QUANTITATIVE_COMPARISON
QUALITATIVE_COMPARISON
TREND
ASSOCIATION
MECHANISTIC_INTERPRETATION
CAUSAL_CLAIM
GENERALIZATION
METHOD_INTERPRETATION
LIMITATION
RECOMMENDATION
```

Support states should distinguish:

```text
DIRECTLY_SUPPORTED
SUPPORTED_WITHIN_SCOPE
CONSISTENT_WITH
SUGGESTIVE
CONFLICTED
INSUFFICIENT_EVIDENCE
NOT_SUPPORTED
```

Method comparison should distinguish:

```text
DIRECTLY_COMPARABLE
COMPARABLE_WITH_QUALIFIERS
COMPLEMENTARY
METHOD_DEPENDENT_DIFFERENCE
NOT_COMPARABLE
INSUFFICIENT_METHOD_METADATA
```

## Provider boundary

DeepSeek may propose bounded structured claims and synthesis using opaque,
authorized evidence references. It may not invent evidence, citations,
numbers, method metadata, conversion, arithmetic, qualification, publication
status, comparison compatibility, or causal authority.

Provider output must be deterministically validated. At most one
validation-guided repair may correct invalid refs, strength, qualifiers,
claim type, or scope mismatch. Repair may not add evidence, search, expand
scope/budget, or alter authoritative inputs.

The same model under evaluation must not define the gold semantics. A model
critic may be diagnostic only.

## Evaluation case contract

Create an offline deterministic case format containing:

```text
case_id
scientific_domain
research_question
authorized Results
authorized LiteratureEvidence
required / allowed / forbidden claims
required qualifiers and limitations
comparison and method expectations
hypothesis expectations
valid stop outcomes
gold-origin authority
```

Gold semantics must test scientific boundaries, not exact wording. Ambiguous
cases are `HUMAN_REVIEW_REQUIRED` and excluded from hard pass/fail.

Build approximately 18–24 high-quality cases spanning:

- trajectory diffusion and condition-limited literature comparison;
- transport plus RDF/coordination association versus causation;
- CrystalNN, VoronoiNN, and cutoff coordination method dependence;
- experimental/theoretical XRD agreement versus phase identification;
- materials ML metrics, chemistry-conditioned error, coverage, and
  generalization;
- PCA/KMeans exploratory outputs without physical-family overclaim;
- supplied electronic structure with external-implementation limits;
- imaginary phonon modes with convergence/finite-size/condition limits;
- condition-explained and genuinely unresolved literature contradictions;
- review versus primary evidence;
- preprint versus published version;
- abstract-only overreach;
- citation-popularity trap;
- missing evidence and failed-search negative-evidence discipline;
- deterministic-only derived arithmetic;
- single-system generalization.

Adversarial cases must tempt causality, mechanism certainty, scope expansion,
method merging, evidence double counting, contradiction collapse, hypothesis
escalation, retracted/abstract overreach, and numeric invention.

## Baseline and defect handling

Run the complete corpus against the current H behavior before scientific
reasoning fixes. Preserve the baseline separately and never overwrite it.

Classify real failures using bounded categories:

```text
QUALITATIVE_SUPPORT
CAUSAL_OVERCLAIM
MECHANISTIC_OVERCLAIM
SCOPE_EXPANSION
METHOD_MISINTERPRETATION
INVALID_COMPARISON
EVIDENCE_DOUBLE_COUNT
CONTRADICTION_COLLAPSE
MISSING_LIMITATION
HYPOTHESIS_ESCALATION
DERIVED_NUMBER_INVENTION
SOURCE_SCOPE_OVERREACH
```

Severity is `CRITICAL | MAJOR | MODERATE | MINOR`.
Fix reusable patterns, not benchmark-specific sentences or prompt keywords.

## Required commands and evidence

Provide:

```text
python scripts/scientific_reasoning_report.py --check
python scripts/scientific_reasoning_report.py --check --live-llm
```

Default evaluation is offline and fixture-backed. Live DeepSeek is optional
for normal CI but required as bounded local acceptance when available.

Generate and retain:

```text
docs/scientific-reasoning/generated/expert_reasoning_baseline.json
docs/scientific-reasoning/generated/expert_reasoning_evaluation.json
```

The final evaluation must expose per-case expected boundaries, actual claims,
support assessments, violations, and outcome, with no hidden reasoning.

Prepare an optional human-review pack containing question, authorized
evidence, synthesis, claim/support map, limitations, and benchmark
expectations. Do not claim independent human validation without an actual
independent materials-science expert review.

## Integration and regression boundaries

- Preserve H numeric grounding, citation identity, abstract scope,
  retraction handling, opt-in/privacy, ScientificResult authority, and
  Capability qualification.
- Preserve A–G lifecycle, Context provenance, bounded autonomy, strategy,
  recovery, cancellation, exact identities, Report, and scientist UX.
- Reasoning assessment may inform strategy but cannot execute Tools.
- Historical interpretation/report output must not be silently rewritten.
- Persist compact reasoning contract/prompt/validator identity where current
  versioning supports it.
- UI changes are allowed only for concise claim status, support,
  counterevidence, method dependence, limitation, or insufficient-evidence
  disclosure. No reasoning trace UI or frontend scientific computation.

## Focused documentation

Create:

```text
docs/scientific-reasoning/SCIENTIFIC_CLAIM_AND_SUPPORT_MODEL.md
docs/scientific-reasoning/METHOD_COMPARISON_AND_INFERENCE_POLICY.md
docs/scientific-reasoning/EXPERT_REASONING_EVALUATION.md
```

Update `docs/index.md`, `docs/13_SHARED_SCHEMA_SPEC.md`,
`PROJECT_STATE.md`, `results.md`, `persistent/DESIGN_PROGRESS.md`,
`persistent/TASK_BOARD.md`, and `TASKS.md` according to repository rules.

## Completion evidence

Report all requested reasoning counts and violation categories, including:

```text
REASONING_EVALUATION_CASES
BASELINE_REASONING_FAILURES
SCIENTIFIC_REASONING_DEFECTS_DISCOVERED / FIXED
REAL_LLM_REASONING_CASES
QUALITATIVE_CLAIM_SUPPORT_VIOLATIONS
CAUSAL_OVERCLAIM_VIOLATIONS
MECHANISTIC_OVERCLAIM_VIOLATIONS
SCOPE_GENERALIZATION_VIOLATIONS
METHOD_COMPARISON_VIOLATIONS
EVIDENCE_INDEPENDENCE_VIOLATIONS
CONTRADICTION_COLLAPSE_VIOLATIONS
HYPOTHESIS_ESCALATION_VIOLATIONS
REQUIRED_LIMITATION_OMISSIONS
DERIVED_NUMERIC_CLAIM_VIOLATIONS
LITERATURE_SCOPE_VIOLATIONS
SCIENTIFIC_AUTHORITY_VIOLATIONS
CORRECT_INSUFFICIENT_EVIDENCE_OUTCOMES
CORRECT_METHOD_DEPENDENCE_OUTCOMES
CORRECT_CONTRADICTION_OUTCOMES
INDEPENDENT_HUMAN_EXPERT_VALIDATION
UNRESOLVED_SCIENTIFIC_REASONING_BLOCKERS
```

Final maturity is one of:

```text
BOUNDED_EXPERT_REVIEW_READY
BOUNDED_REASONING_READY
PARTIAL
NOT_READY
```

Never use `EXPERT_VALIDATED` without actual independent expert review.
Choose Workstream J only from measured evidence.
