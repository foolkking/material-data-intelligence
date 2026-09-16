# Adjudication Protocol

Do not average away scientific disagreement.

## Material disagreement

Escalate when overall verdicts differ by at least two levels, a critical
dimension differs by at least two points, claim support differs between
supported and insufficient/unsupported, or reviewers disagree about causal
support or comparison validity.

## Third review

Assign a third competent reviewer who sees neither prior score nor comments.
The third review is independent and uses the same frozen packet.

## Structured adjudication

If disagreement remains, discuss only the claim, exact evidence, method,
conditions, scope and relevant limitation. Record one of:

```text
ADJUDICATED_ACCEPTABLE
ADJUDICATED_MAJOR_DEFECT
ADJUDICATED_CRITICAL_DEFECT
GENUINE_SCIENTIFIC_DISAGREEMENT
CASE_SPECIFICATION_PROBLEM
```

`GENUINE_SCIENTIFIC_DISAGREEMENT` is retained when the evidence permits
qualified expert disagreement and the System Response itself preserves the
uncertainty. Reviewer seniority, citation count and majority prestige are not
adjudication authorities.

## Maturity gates

Full validation requires at least three independent reviewers, 24 valid
scored cases, two reviewers per normal case, three per anchor, zero
adjudicated critical failures, no rejects, at least 22 acceptable-or-minor
cases, at least 16 accepts, critical-dimension medians at least 4.0, domain
floors, research-decision usefulness at least 80%, and target
Krippendorff alpha at least 0.60. A missing human submission leaves J in
`REVIEW_READY`, never in automated PASS.

