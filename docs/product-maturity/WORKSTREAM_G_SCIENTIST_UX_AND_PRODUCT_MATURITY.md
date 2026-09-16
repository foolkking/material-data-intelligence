# Workstream G — Scientist UX & Product Maturity

## Status and repository authority

- Authorized on: 2026-09-10
- Canonical active repository: `E:\1project\mdi-b0-5a1`
- Historical comparison/recovery source only: `E:\1project\Material Data Intelligence`
- Workstreams A–F are accepted foundations and must not be redesigned.

## Mission

Turn the durable lifecycle, provenance-aware context, capability platform,
scientific qualification, bounded autonomy, and research strategy established
in Workstreams A–F into one coherent scientist-facing Research product.

A materials researcher must be able to ask a question, follow a multi-cycle
investigation, understand evidence and limitations, control execution, compare
compatible Results, recover from failure, reopen historical work, and remain in
control without learning Agent, Tool, worker, or persistence internals.

This is product-maturity work, not a visual redesign and not a new Research,
Workspace, lifecycle, strategy, or viewer architecture.

## Required execution sequence

1. Run a bounded current-product walkthrough against the canonical runtime.
2. Cover normal, autonomous, clarification, cross-family, reuse, hypothesis,
   insufficient-evidence, cancellation, recovery, historical reopen,
   comparison, Report, and mobile paths where current persisted fixtures allow.
3. Record an evidence-backed UX audit before making product implementation
   changes.
4. Fix only concrete scientist-facing gaps found in the walkthrough.
5. Add focused regression and acceptance coverage.
6. Verify canonical API, workers, frontend, persistence, and browser behavior.
7. Generate machine-readable acceptance evidence and reconcile canonical
   project authorities.

## Scientist-facing mental model

The primary product model is:

```text
Research question
→ Sources / data
→ Research progress
→ Scientific evidence
→ Findings
→ What remains uncertain
→ Optional next research
```

Normal surfaces must not require users to reason about `ResearchTurn`, `Job`,
`ToolCall`, capability resolution, projector internals, queues, raw IDs, or
ContextSnapshot identities. Those details may appear only through advanced
provenance where scientifically or operationally useful.

## Product contracts

### Conversation and timeline

- Research remains conversation-centered.
- The Research Timeline is the primary visible representation of multi-cycle
  work and shows meaningful scientific events rather than raw operational logs.
- Completed operational detail collapses naturally.
- No fixed global right-side activity rail may be reintroduced.
- Current main question and, when relevant, current subquestion are visible.

### Research map and scientific resolution

- Expose a compact Research Map from durable A–F projections.
- Show questions as resolved, partially addressed, unresolved, or not
  answerable from current evidence.
- Link questions to key Results, limitations, and active hypotheses.
- The map is not chain-of-thought, a planner trace, or a graph editor.

### Hypotheses, evidence gaps, continuation, and stopping

- Observation, Interpretation, Finding, and Hypothesis must remain distinct.
- Hypotheses show explicit status, evidence, and causal/qualification limits.
- Preserve hypothesis evolution rather than silently deleting old states.
- Show the current evidence gap and why the next analysis is useful.
- Show typed scientist-facing stop outcomes that distinguish completion,
  clarification, evidence limits, unavailable capability, budget limits,
  cancellation, and failure.

### Clarification

- Clarification is a first-class conversational continuation.
- Questions are specific, bounded, scientifically motivated, and based on
  authorized choices.
- Users must not need internal IDs.
- The original question, prior evidence, and research branch remain intact
  after the answer.

### Controls

The product must communicate distinct semantics for:

- **Stop research**: prevent future autonomous cycles and preserve completed
  science.
- **Cancel active analysis**: request cancellation of currently running work;
  completed Results remain.
- **Continue**: resume or extend the current research objective.
- **Retry failed analysis**: resume from the latest durable safe boundary and
  reuse completed upstream Results.
- **Run again**: intentional recomputation.
- **Reinterpret**: produce a new explanation from an existing Result without
  recomputation.
- **Edit question / Branch research**: preserve immutable historical research
  and create a related revised branch.
- **Start new research**: create an unrelated research context.

Controls with different semantics must not share ambiguous labels or behavior.

### History and reopen

- Research history uses meaningful scientist-facing titles.
- Users can identify the question, branch, analyses performed, findings,
  unresolved issues, and current state.
- Long-running, failed, cancelled, and completed Research reopens from durable
  state without requiring an open browser tab.
- Tasks/notifications return to the exact Research context where possible.

### Results, evidence, and provenance

- Preserve result-first hierarchy: meaning, scientific detail, provenance,
  developer details.
- Multi-result research uses concise scan-friendly Result summaries.
- Important limitations appear near findings rather than only in advanced
  panels.
- Show human-readable source and exact version semantics without UUIDs by
  default.
- Scientific qualification is disclosed in plain scientific language where
  it affects trust.
- Advanced provenance may expose exact version, capability, Tool/Adapter
  version, parameters, Artifact, Result, qualification fingerprint, and
  Context refs, but never secrets, raw prompts, hidden reasoning, or irrelevant
  worker internals.

### Comparison

- Compatible scientific Results can be reviewed side-by-side.
- Compatibility must account for quantity, unit, method, normalization,
  conditions, and source type using existing F authorities.
- Incompatible comparisons are blocked or clearly explained; the browser must
  not invent scientific normalization.
- Findings are separated from possible explanations.

### Failure and recovery

- Failure states explain what happened, what science was preserved, and the
  correct next action.
- Partial success remains usable.
- Recovery actions preserve upstream Results and target only the failed durable
  boundary.
- User cancellation is neutral rather than presented as a system error.

### Autonomy

- Standard and bounded multi-step modes are clearly distinguished.
- Bounded mode explains that additional justified analyses may run within
  fixed limits and will stop when addressed, unsupported, or budget-bound.
- During execution show current question, analysis, rationale, and completed
  evidence without exposing future speculative plans.
- Users control goal and boundaries without approving individual Tool calls.

### Reports and workbench

- Workbench remains scientific: Source, Data, Result, Comparison, Evidence,
  Report, Inspector.
- Reports summarize question, sources, analyses, findings, comparisons,
  hypotheses/interpretations, limitations, unresolved questions, methods, and
  provenance—not Agent trace.
- Report statements remain linked to authoritative Results.
- Workspace remains a presentation/recovery projection and cannot override
  scientific or lifecycle authorities.

### Responsive, performance, and accessibility

- Preserve the established desktop independent-scrolling and mobile
  single-primary-pane patterns.
- New Research Map, hypotheses, controls, and comparison surfaces work at
  approximately `390x844` without page-level horizontal overflow.
- Long histories collapse completed cycles; heavy viewers remain lazy and
  clean up resources.
- Preserve keyboard access, visible focus, semantic headings, accessible
  names, useful live status, non-color-only state, 200% zoom/reflow, reduced
  motion, touch targets, and scientific visualization alternatives.

## Authority and scope prohibitions

- Frontend code may format and present authoritative data but may not calculate
  new scientific metrics, comparisons, qualification, or interpretation.
- UI state cannot override ScientificObjectVersion, ScientificResult,
  ResearchTurn, Context, strategy, qualification, or execution state.
- Do not redesign Phase 12 navigation, Workspace, viewers, responsive
  architecture, accessibility foundation, or design system unless a concrete
  observed defect requires a bounded correction.
- Do not create a giant Research component, another activity rail, another
  lifecycle, another Workspace, a new scientific computation path, or hidden
  reasoning exposure.
- Do not use the old repository, push, deploy, or perform release
  qualification.

## Required journeys

Acceptance must cover, through focused deterministic tests and real browser
evidence as practical:

1. normal Research;
2. bounded multi-step Research;
3. clarification;
4. ML-to-composition cross-family Research;
5. existing Result reuse;
6. compatible comparison;
7. incompatible comparison;
8. hypothesis creation and status evolution;
9. insufficient-evidence stop;
10. downstream failure and durable recovery;
11. cancellation with completed Results preserved;
12. edit/branch continuity;
13. historical reopen;
14. multi-cycle Report and source review;
15. mobile Research at `390x844`.

Use real canonical persisted data and services where safe. Live provider use is
required only for journeys that genuinely need provider behavior.

## Acceptance evidence

Generate `docs/product-maturity/generated/scientist_ux_acceptance.json` from the
actual acceptance run. It must report at least:

```text
SCIENTIST_UX_JOURNEYS
REAL_BROWSER_JOURNEYS
MOBILE_JOURNEYS
CLARIFICATION_JOURNEYS
COMPARISON_JOURNEYS
RECOVERY_JOURNEYS
HISTORICAL_REOPEN_JOURNEYS
RAW_INTERNAL_ID_DEFAULT_EXPOSURES
MOBILE_BLOCKING_OVERFLOW
FATAL_BROWSER_ERRORS
SCIENTIFIC_AUTHORITY_UI_VIOLATIONS
UNRESOLVED_PRODUCT_MATURITY_BLOCKERS
```

Preserve Workstream F/A/E regression expectations:

```text
IRRELEVANT_CAPABILITY_EXECUTIONS = 0
REDUNDANT_EXECUTIONS = 0
QUALIFICATION_POLICY_VIOLATIONS = 0
UNSUPPORTED_CLAIM_VIOLATIONS = 0
HYPOTHESIS_OVERCLAIM_VIOLATIONS = 0
```

## Completion authority

Completion requires focused code tests/builds, canonical real-browser journeys,
mobile verification, accessibility regression evidence, generated acceptance
evidence, and updates to `PROJECT_STATE.md`, `results.md`,
`persistent/DESIGN_PROGRESS.md`, and `persistent/TASK_BOARD.md`.

The final assessment must directly answer the twenty product questions in the
authorizing prompt, assign:

```text
SCIENTIST_PRODUCT_MATURITY =
READY_FOR_BOUNDED_SCIENTIST_USE | CONDITIONAL | PARTIAL | NOT_READY
```

and choose Workstream H from measured product/scientific bottlenecks rather
than naming order.
