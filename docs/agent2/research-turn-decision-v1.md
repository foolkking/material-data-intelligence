# ResearchTurnDecision 1.0

`ResearchTurnDecision` is the validated boundary between conversation
understanding and future planning/execution.

```text
contract_version = 1.0
action
assistant_message
research_objective
selected_scope_ref_keys[]
scientific_requirements[]
reusable_result_ref_keys[]
clarification
confidence
```

All models use `extra="forbid"`; key lists reject duplicates. Object keys may
be selected or used as requirement subjects. Result keys may only be reused.
Every Requirement ID must be active in the bounded Phase 2 registry, compatible
with its object type, and valid against its constraint JSON Schema.

## Routing status

| Action | Phase 2 routing | Turn status |
|---|---|---|
| `ANSWER` | final assistant message | `ANSWERED` |
| `CLARIFY` | one clarification message | `NEEDS_CLARIFICATION` |
| `ANALYZE` | pre-run message and validated requirements | `READY_TO_PLAN` |
| `CONTINUE_ANALYSIS` | prior Result/Turn relation and validated requirements | `READY_TO_PLAN` |
| `INTERPRET_RESULT` | classification only | `ORCHESTRATING` |
| `QUERY_DATA`, `MANAGE_DATA`, `OPEN_OBJECT`, `CREATE_REPORT`, `UPDATE_REPORT`, `EXPORT` | classification only | `ORCHESTRATING` |

Classification-only actions receive `READY_FOR_DOWNSTREAM`; they are not
reported as completed. `ANSWER` and `CLARIFY` receive `COMPLETED` because the
Phase 2 user-facing action itself is complete.

Migration `0018_agent2_orchestration_decisions` adds one immutable accepted
decision per Turn. `decision_json` is authoritative audit data;
`research_turns.action_type` is its consistent fast projection. Provider and
model metadata are internal and omitted from normal Turn reads and SSE.
