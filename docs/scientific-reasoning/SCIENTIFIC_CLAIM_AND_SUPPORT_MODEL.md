# Scientific Claim and Support Model

## Purpose

Workstream I adds a bounded **claim-support assessment** over existing
scientific authorities. It answers whether a proposed statement is warranted
by the authorized evidence at its stated strength, scope and methodological
level. It does not create a scientific truth store.

```text
ScientificResult != LiteratureEvidence != Interpretation != Hypothesis
                 != CapabilityQualification
```

- `ScientificResult` remains the authority for platform-computed output.
- `LiteratureEvidence` remains an exact, scope-limited external source
  projection.
- `Interpretation` and Report prose communicate accepted evidence; they are not
  new evidence.
- `Hypothesis` remains non-authoritative, including when literature motivates
  it.
- Capability qualification remains governed only by Workstream D evidence.

## Contracts

`scientific-reasoning/1.0` defines a bounded read-only `ReasoningEvidence` and
provider-safe `ProposedScientificClaim`. The deterministic
`ClaimSupportAssessment` records only observable scientific decision
provenance:

- claim type and support status;
- supporting and contradicting opaque references;
- asserted scope and method context;
- comparison status, necessary qualifiers and limitations;
- common-lineage independence count;
- reason codes, defect types and bounded severity;
- contract and policy versions plus a stable assessment fingerprint.

No provider scratchpad, prompt, hidden reasoning trace or private source
identifier is persisted.

### Claim types

The vocabulary is deliberately small:

`DIRECT_OBSERVATION`, `DESCRIPTIVE_SYNTHESIS`,
`QUANTITATIVE_COMPARISON`, `QUALITATIVE_COMPARISON`, `TREND`,
`ASSOCIATION`, `MECHANISTIC_INTERPRETATION`, `CAUSAL_CLAIM`,
`GENERALIZATION`, `METHOD_INTERPRETATION`, `LIMITATION` and
`RECOMMENDATION`.

### Support statuses

`DIRECTLY_SUPPORTED`, `SUPPORTED_WITHIN_SCOPE`, `CONSISTENT_WITH`,
`SUGGESTIVE`, `CONFLICTED`, `INSUFFICIENT_EVIDENCE` and `NOT_SUPPORTED`
express epistemic status, not probability or universal confidence.

## Core policy

The assessor fails closed for unknown evidence and applies reusable scientific
boundaries:

- causal claims require explicit causal-design authority; the platform does
  not provide a general causal-inference authority;
- a mechanism remains tentative unless the selected evidence supports the
  stated scope; a one-source mechanism is at most a hypothesis;
- a studied material, split, trajectory or abstract cannot authorize a
  universal generalization;
- a bounded failed search is absence of identified support, not proof of
  universal absence;
- `ABSTRACT_ONLY` evidence cannot support unseen figure, table, supplement or
  method detail;
- retracted or withdrawn work cannot provide ordinary support;
- literature cannot promote a Capability qualification;
- citation count is a discovery signal, never a truth authority;
- exploratory clusters or outliers do not establish physical invalidity;
- external-solver semantic integration does not independently validate that
  upstream solver.

The policy records a limitation at the claim it constrains. A rejected proposed
claim is excluded from a repaired synthesis; it is not silently reworded as a
stronger conclusion.

## Independence, contradictions and scope

Evidence is grouped by explicit lineage. A trajectory MSD result and a derived
diffusion result can report different quantities but are not independent
datasets. A preprint and its published version, or a primary paper and a review
summarizing it, must not become multiple independent confirmations.

When sources differ, the assessment first preserves known scope, condition and
method differences. If they explain the difference, the outcome is
condition- or method-dependent rather than a winner-take-all conclusion. If
metadata cannot resolve it, the outcome remains `CONFLICTED` or
`INSUFFICIENT_EVIDENCE`.

## Integration and versioning

Interpretation contract `1.1` may carry only server-generated accepted
assessments. Report contract `2.0` propagates an assessment with each finding
and rejects a finding whose assessment is not accepted. Historical records
retain their existing interpretation/report snapshots; a newer reasoning
contract produces a new projection rather than rewriting historical science.

The synthesis path permits at most one validation-guided provider repair. A
repair may remove or correct an unsupported claim, qualifier, scope or evidence
reference. It may not add evidence, search externally, derive a new number,
change a Result, expand scope or alter qualification.
