# Phase 10L-2 Capability-Aware Planner Contract

## Purpose

Phase 10L-2 places a deterministic eligibility and binding gate between a
persisted READY `AnalysisIntent 1.0` and the existing `AnalysisPlan 0.1`.
It does not change plan syntax, Registry execution authority, PlanValidator,
or QueueWorkerRuntime.

```text
READY AnalysisIntent 1.0
  + exact Material Data Profile 2.0
  + validated Registry snapshot
  -> Eligibility Resolution 1.0
  -> eligible-only candidate projection
  -> Capability Decision 1.0
  -> exact parameter binding
  -> capability-context validation
  -> unchanged AnalysisPlan 0.1
```

Only `PLAN_READY` can continue to plan/job persistence and enqueue. The other
typed outcomes are `NEEDS_CLARIFICATION`, `UNSUPPORTED`,
`CAPABILITY_MISMATCH`, and `VALIDATION_FAILED`.

## Registry Planner Metadata

Every one of the 53 current Registry entries has strict planner metadata. The
metadata records stable tool/version identity, availability, supported
AnalysisIntent vocabulary, accepted object kinds, required Profile facts,
target roles, deterministic parameter bindings, declared existing artifact
types, bounded cost, independent-composition status, and an optional collision
group. Thirty-eight current tools are selectable; deployment-unavailable and
Future entries remain evaluated but cannot be eligible. Not Planned entries
cannot become selectable.

Metadata is validated against each Tool Registry input schema, parameter
schema, artifact declarations, adapter ownership, and cardinality. Unknown
fields, executable metadata, invalid bindings, impossible cardinality, and
selectable Future/Not Planned declarations are rejected. Registry insertion
order has no semantic authority.

## Eligibility Resolution 1.0

The immutable resolution binds the exact Intent ID/hash, Profile
ID/version/semantic hash, dataset version, resource hashes, and deterministic
Registry snapshot ID/hash. It records every evaluated candidate, eligible and
rejected IDs, typed reasons, matched intent/need/output codes, exact target and
resource identities, parameter domains, rank facts, diagnostics, and resolver
provenance.

Every mandatory eligibility rule is explicit. A candidate must exist, be
available, accept the exact object kind, satisfy required Profile and target
facts, support the structured intent/needs/output, expose complete bounded
binding domains, and remain inside safety and cardinality boundaries. Failed
candidates are retained with typed reasons rather than silently omitted.

## Candidate Projection and Selection

Planner providers receive only the eligible projection: stable tool identity,
coverage facts, exact resources/targets, allowed binding domains, cost, and
collision/composition facts. They do not receive rejected tools, Future/Not
Planned entries, the full Registry, paths, code, secrets, or unbounded Profile
data.

Deterministic selection ranks only eligible candidates by intent coverage,
capability-need coverage, desired-output coverage, exact applicability,
binding completeness, warnings, bounded cost, and stable tool/version tie
break. It does not inspect raw-goal substrings or Registry/column/display order.
At most four independent selections are permitted, and no dependency or prior
artifact reference can be emitted.

## Exact Binding and Validation

Parameter values come only from exact Intent resources/targets/groups, exact
Profile facts, bounded Registry literals, or repository-owned declared
defaults. Each bound value retains its source and source identity. First-column
selection, fuzzy labels, guessed units, arbitrary LLM IDs, paths, URLs, shell,
SQL, and executable text are prohibited.

The independent capability-context validator recomputes identities and checks
Intent/Profile/Registry freshness, eligibility membership, exact coverage,
binding domains and provenance, collisions, independent composition, plan
steps and inputs, and absence of dependency/artifact-binding fields. The
unchanged PlanValidator then validates the generated AnalysisPlan 0.1.

## Optional LLM Path

The existing OpenAI-compatible transport may receive the eligible projection
and strict selection schema. It must return one bare JSON object. Markdown,
prose, duplicate keys, unknown fields, invented identities, ineligible tools,
out-of-domain values, dependencies, and executable content fail closed. There
is no Mock fallback.

One validation-guided repair is allowed only after strict parsing succeeds and
the capability validator returns a repairable diagnostic. Repair uses the same
candidate and binding domains and cannot change the Intent. A failed repair is
terminal `VALIDATION_FAILED`; default CI uses `REAL_LLM_CALLS = 0`.
