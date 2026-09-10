# Hypothesis and Evidence Policy

## Authority

`ScientificObjectVersion`, `Artifact` and `ScientificResult` remain scientific
authorities. `ResearchEvidenceState` and `ResearchStrategyDecision` are
derived strategy projections. A hypothesis, interpretation, report, memory
item or UI state cannot become a fact merely because the Agent generated it.

## Evidence hierarchy

1. Exact authorized ScientificObjectVersion inputs.
2. ScientificResult facts and evidence grounded in those versions.
3. Derived Results with visible parent/lineage relationships.
4. Grounded Interpretation for semantic organization.
5. Research Memory and user assertions for continuity or intent.
6. Reports and Workspace for communication/presentation only.

Repeated prose or transformations of one Result do not count as independent
evidence.

## Hypothesis rules

A hypothesis must be tied to an active bounded question, cite supporting and/or
contradicting Result identities, state testable predictions or explicit
non-testability, and preserve assumptions and method limitations.

Allowed statuses are `PROPOSED`, `PARTIALLY_SUPPORTED`,
`SUPPORTED_WITHIN_SCOPE`, `CONTRADICTED`, `UNRESOLVED` and
`NOT_TESTABLE_WITH_AVAILABLE_CAPABILITIES`. Strategy may use a hypothesis to
request discriminating evidence, but may not use the hypothesis itself as
evidence.

## Minimum sufficient evidence

Strategy prefers the smallest qualified evidence set that addresses the user
objective. It should stop when the objective is answered, when another
analysis is redundant, or when the requested claim is outside available
evidence. More available Tools are not a reason to run more work.

## Comparison and contradiction

Before comparing two observations, strategy checks quantity predicate, unit
dimension, method/parameter semantics, source type, relevant conditions and
exact source identity. Incompatible or under-specified Results are not
silently averaged or ranked.

Contradictions are classified as different exact versions, methods, parameter
conventions, applicability domains, units, numerical tolerance or genuine
unresolved disagreement. Explainable differences should be resolved through
metadata. Genuine conflicts remain visible and normally cause
`CONFLICTING_EVIDENCE` or bounded clarification.

## Provider and memory safety

Provider proposals can reference only identifiers supplied in the current
bounded context. They undergo deterministic validation and at most one repair.
No hidden reasoning is persisted.

Strategy continuity may be written as a typed, source-grounded memory item
such as an open question or decision. It must not replace the Result
authority, cross project boundaries, or silently upgrade stale or
external-semantics evidence.
