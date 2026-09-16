# Expert Scientific Reasoning Evaluation

## Evaluation-first method

The repository-owned corpus is evaluated before reasoning improvements and
retained afterward. Gold semantics specify required/allowed/forbidden claims,
qualifiers, limitations, comparison expectations and acceptable stop outcomes;
they do not prescribe exact prose.

- Corpus: `fixtures/expert_reasoning_cases_v1.json`
- Immutable pre-fix baseline: `generated/expert_reasoning_baseline.json`
- Current generated evaluation: `generated/expert_reasoning_evaluation.json`
- Deterministic command: `python scripts/scientific_reasoning_report.py --check`
- Optional bounded live-provider command:
  `python scripts/scientific_reasoning_report.py --check --live-llm`
- Representative PostgreSQL rollback smoke:
  `python scripts/scientific_reasoning_service_smoke.py --check`

Default evaluation is offline and fixture-backed. Live DeepSeek evaluation is
not a CI requirement and is not the source of gold labels.

## Corpus and baseline

The initial corpus has 27 cases spanning trajectory/diffusion, transport plus
structure, coordination methods, XRD, materials ML, composition space,
electronic structure, phonons, contradicting literature, review/primary and
preprint/published dependence, abstract-only scope, citation popularity,
missing evidence, derived arithmetic, generalization, retraction and
qualification boundaries.

Before the I contracts were introduced, the same corpus accepted 22 invalid or
insufficiently constrained claims. These baseline failures were preserved and
classified across qualitative support, causal/mechanistic overclaim, scope
expansion, method/comparison error, evidence double count, contradiction
collapse, missing limitation, hypothesis escalation, numeric invention,
source-scope overreach and scientific-authority defects.

## Current acceptance evidence

The generated final report records:

```text
REASONING_EVALUATION_CASES = 27
BASELINE_REASONING_FAILURES = 22
SCIENTIFIC_REASONING_DEFECTS_DISCOVERED = 22
SCIENTIFIC_REASONING_DEFECTS_FIXED = 22
REAL_LLM_REASONING_CASES = 5
CROSS_DOMAIN_REASONING_CASES = 8
all tracked final violation counts = 0
CORRECT_INSUFFICIENT_EVIDENCE_OUTCOMES = 17/17
CORRECT_METHOD_DEPENDENCE_OUTCOMES = 1/1
CORRECT_CONTRADICTION_OUTCOMES = 2/2
INDEPENDENT_HUMAN_EXPERT_VALIDATION = NO
```

Five sanitized live DeepSeek cases covered transport/structure, ML/composition,
XRD, literature contradiction and phonon limitations. Live output varied during
initial evaluation: unsupported scope/limitation behavior and one multiple-JSON
provider response were observed. The bounded provider retry, one repair and
deterministic claim assessment prevented unsupported material from reaching the
accepted synthesis. The final recorded live run passed 5/5, with repair used in
2/5 cases. This is a regression signal, not a population reliability estimate.

Focused tests passed: 108 passed, 5 skipped across reasoning/knowledge/
interpretation/report suites; 36 passed, 2 skipped across bounded autonomy,
strategy and product regressions. Ruff, compileall and focused diff checks
passed. The real PostgreSQL smoke persisted and reopened a Result snapshot,
Interpretation 1.1 and Report 2.0 in a rollback-only transaction while
preserving the assessment fingerprint and no hidden reasoning.

## Human review pack

`generated/human_review_pack.json` contains a small optional, evidence-limited
review set. It includes the research question, authorized evidence summary,
accepted/rejected boundary, expected limitation and reviewer prompt, but no
raw prompts, hidden reasoning, secrets or internal database IDs.

The resulting maturity claim is `BOUNDED_EXPERT_REVIEW_READY`, not
`EXPERT_VALIDATED`. Independent materials-scientist review remains necessary
before making a stronger claim.
