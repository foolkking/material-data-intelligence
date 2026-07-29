# Phase 10L-1 AnalysisIntent v1 Contract

## Boundary

`AnalysisIntent` is an inert, independently versioned request contract between
an exact Material Data Profile 2.0 revision and the existing Planner. It does
not select tools, rank capabilities, change `AnalysisPlan 0.1`, or execute work.

The checked-in authorities are:

* Python: `packages/schemas/mdi_schemas/analysis_intent.py`
* JSON Schema: `packages/schemas/json/analysis-intent-v1.schema.json`
* TypeScript: `packages/schemas/src/index.ts`

The schema version is `1.0`. Unknown fields are rejected.

## Identity

Every intent has `intentId` and `intentHash`. The hash is SHA-256 over UTF-8
canonical JSON with sorted keys, compact separators, and unescaped Unicode.
Runtime identity fields (`intentId`, `intentHash`) and
`provenance.createdAt` are excluded. The ID is
`intent_<first 24 hash hex characters>`. Repeated semantic input is idempotent;
a clarification creates a new immutable hash/ID and records its parent.

## Required Semantics

The contract retains a bounded, secret-redacted `rawGoal` and a conservative
whitespace-normalized `normalizedGoal`. It binds exact dataset version,
Profile 2.0 contract and semantic hash, resource object ID/type/hash/kind, and
Profile-derived target semantics. It separately records scientific intents,
desired outputs, typed constraints, required/optional capability needs,
ambiguities, missing facts, unsupported reasons, provenance, and warnings.

The vocabulary is bounded to dataset, composition/property, comparison,
composition-space, structure, trajectory, phonon, reciprocal, volumetric,
materials-ML, sample inspection, visualization, and report/export intents.
Future, Not Planned, external compute, and arbitrary execution requests do not
gain free-form supported intent identities.

## Outcomes

* `READY`: exact Profile/scope facts exist and no blocking ambiguity remains.
* `NEEDS_CLARIFICATION`: one answer over Profile-derived candidates can resolve
  all blocking ambiguity.
* `UNSUPPORTED`: data is absent, the request crosses a product/security
  boundary, or bounded clarification cannot resolve it.

`READY` means only that the existing Planner may be invoked. It is not a tool
availability, AnalysisPlan validation, enqueue, or execution claim.
