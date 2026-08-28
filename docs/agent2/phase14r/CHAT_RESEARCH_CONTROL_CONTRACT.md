# Chat / Research Control Contract

## Re-interpret existing scientific results

Modern ResearchTurn presentations may offer `重新解释（不重算科学结果）`
when the user is inside an authorized Research Session. The control creates a
new immutable ResearchTurn carrying the prior Result identity in its explicit
context and routes through the normal Agent2 action router. It never mutates
the historical Turn and cannot directly enqueue scientific work. If reuse is
not eligible, the existing router/planner semantics remain authoritative and
must fail closed or perform an explicitly new analysis.

Research controls are explicit actions over immutable execution history:

* Edit latest user message → new message revision and new ResearchTurn branch.
* Branch → preserves the old branch and exact source/result identities.
* Stop planning/orchestration → `CANCELED` with no Job where possible.
* Stop queued/running work → `CANCELING` then `CANCELED` or `PARTIAL`.
* Continue → reuses authorized session context and exact valid Results when
  eligible.
* Rerun → creates a new execution lineage and never overwrites old evidence.
* Re-interpret → changes only grounded narrative; Job/ToolCall/Artifact/Result
  deltas must all be zero.
* Retry → explicit new attempt or bounded failed-step retry, preserving the
  failed record.

The existing backend cancellation boundary is
`ResearchTurnService.cancel_turn` and
`/api/research/turns/{turn_id}/cancel`. The complete message-revision,
branch-switching and distinct Continue/Rerun/Re-interpret UI contract remains
not yet qualified.
