# Agent 2.0 Phase 2 State Flow

```text
POST Turn
  -> RECEIVED
  -> Redis/RQ wakeup(turn_id) when explicitly enabled
  -> CAS RECEIVED -> RESOLVING_CONTEXT
  -> deterministic authorized candidate assembly
  -> immutable ResearchContextSnapshot
  -> ORCHESTRATING
  -> DeepSeek structured decision outside DB transaction
  -> validation + authorization re-check
     -> ANSWERED
     -> NEEDS_CLARIFICATION
     -> READY_TO_PLAN
     -> ORCHESTRATING + READY_FOR_DOWNSTREAM (classification only)
     -> FAILED (typed safe error)
```

`NEEDS_CLARIFICATION` is terminal. A reply creates a new child Turn whose
`parent_turn_id` references the clarification Turn. `CONTINUE_ANALYSIS` records
the exact prior Result Turn in `continuation_of_turn_id` when resolved.

Phase 2 emits persisted domain events and projects them to product SSE names:
`context.resolving`, `context.ready`, `assistant.preparing`,
`assistant.message`, `assistant.clarification`, `analysis.ready_to_plan`,
`turn.answered`, and `turn.failed`. Internal provider calls, token usage,
validation mechanics, and chain-of-thought are not product events.

No Phase 2 route creates an AnalysisPlan, Job, ToolCall, Artifact, scientific
interpretation, Report, or destructive data operation.
