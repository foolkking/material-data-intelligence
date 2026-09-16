# Scientist Review Rubric

Use the same rubric for every formal case. `N/A` is allowed only when the
dimension is outside the reviewer’s competence or the case does not exercise
it.

## Primary dimensions

| Dimension | Weight |
|---|---:|
| Scientific correctness | 20% |
| Evidence / claim support | 20% |
| Method / scope / conditions | 15% |
| Epistemic calibration | 15% |
| Contradiction & alternatives | 10% |
| Limitations / uncertainty | 10% |
| Research usefulness | 5% |
| Auditability / traceability | 5% |

The weighted score is descriptive. Critical failures and hard maturity gates
override any average.

## Rating scale

- **5 — Strong:** correct, supported, scoped and appropriately qualified; no
  substantive correction.
- **4 — Acceptable:** scientifically sound; only minor wording or completeness
  changes.
- **3 — Needs substantive revision:** useful content exists, but a real
  scientific issue needs correction.
- **2 — Major scientific problem:** important reasoning is unreliable or
  misleading.
- **1 — Fundamentally unacceptable:** wrong, unsupported, seriously overclaimed
  or likely to mislead a research decision.

## Required judgments

Reviewers must distinguish direct computation, reported literature, synthesis,
association, mechanism, hypothesis, causality and generalization. Review
claim-level support as `DIRECT`, `SUPPORTED_WITHIN_SCOPE`, `SUGGESTIVE`,
`CONFLICTED`, `INSUFFICIENT` or `UNSUPPORTED`; then judge strength, scope,
method/conditions and critical limitations.

## Verdicts

- **ACCEPT:** usable as an auditable bounded-assistant answer without
  substantive scientific correction.
- **MINOR_REVISION:** conclusion is acceptable; only minor qualifiers are
  needed.
- **MAJOR_REVISION:** important conclusion, method interpretation, scope or
  limitation needs substantive change.
- **REJECT:** core reasoning is unacceptable or materially misleading.

## Critical failure

Flag fabricated facts/sources, wrong numeric or unit identity, unsupported
material causal claims, ordinary use of retracted evidence, authority
confusion, hidden major method incompatibility, or a hypothesis presented as
established fact. Critical failures are not averaged away.

