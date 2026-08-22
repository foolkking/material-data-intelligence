# ResearchTurn Contract v1

`ResearchTurn` is a user-level research action. It is deliberately separate
from `Job`, `AnalysisPlan`, `ToolCall`, and the existing Research Session and
Research Message tables.

## Receive transaction

`POST /api/projects/{project_id}/research/sessions/{session_id}/turns` performs
one short transaction: authorize Project and Session, persist one existing
`messages` row with role `user`, allocate a session-locked sequence, persist a
`RECEIVED` turn, append `TURN_RECEIVED`, and return `202`. It creates zero
Planner, Plan, Job, ToolCall, Artifact, or provider records.

The request is:

```json
{
  "message": "Inspect this structure",
  "ui_context": {
    "active_object_refs": [],
    "selection_refs": []
  },
  "reply_to_turn_id": null
}
```

The server re-authorizes all UI references and verifies reply scope.

## Lifecycle

The implemented state authority is `research_agent/turns/state_machine.py`.
The deterministic Phase 1 path is:

```text
RECEIVED -> RESOLVING_CONTEXT -> ORCHESTRATING
```

Infrastructure failure may move the first five non-terminal planning states to
`FAILED`; cancellation is supported for `RECEIVED`, context resolution,
orchestration, and planning states. Clarification, answer, unsupported,
plan-rejected, completed, partial, failed, and canceled states are terminal.
A clarification is a new child turn, never a revival of the old turn.

## Read and event API

- `GET /api/research/turns/{turn_id}`
- `GET /api/projects/{project_id}/research/sessions/{session_id}/turns?cursor=&limit=`
- `POST /api/research/turns/{turn_id}/cancel`
- `GET /api/research/turns/{turn_id}/events`

Turn reads return bounded messages, context summary, result availability, and
timestamps. SSE re-authorizes on every connection and emits persisted turn
events with monotonic sequence IDs; `Last-Event-ID` resumes without replaying
earlier events.

## Context snapshot

`ResearchContextSnapshot` is immutable and unique per turn. Phase 1 stores
active scope, selection, explicit resolved references, result IDs, constraints,
goal, unresolved questions, a deterministic fingerprint, and compiler version.
The stub resolver stops at `ORCHESTRATING`; it does not call an LLM or invent
an action decision.
