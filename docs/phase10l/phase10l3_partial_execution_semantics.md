# Phase 10L-3 Partial Execution Semantics

## Step States

`PENDING`, `READY`, `RUNNING`, `SUCCEEDED`, `FAILED`,
`BLOCKED_DEPENDENCY`, and `NOT_STARTED` are explicit execution states.

- Adapter or pre-invocation binding failure marks the affected step `FAILED`.
- A step whose required producer did not succeed is
  `BLOCKED_DEPENDENCY`; its Adapter is not invoked.
- Runtime validation failure marks all steps `NOT_STARTED`.
- Blocked state is not represented as an Adapter failure.

## Binding States

Bindings use `PENDING`, `RESOLVED`, `FAILED_PRODUCER`, `MISSING_ARTIFACT`,
`CONTRACT_MISMATCH`, `SCOPE_MISMATCH`, `CHECKSUM_MISMATCH`, `SIZE_REJECTED`,
or `CONSUMER_NOT_RUN`.

## Branch Rules

1. A successful producer makes only its valid outgoing bindings resolvable.
2. A failed producer blocks its direct and transitive descendants.
3. A binding error fails the consumer before Adapter invocation and blocks its
   descendants.
4. A consumer Adapter failure does not delete upstream artifacts.
5. Independent branches continue in deterministic topological order.
6. Every artifact produced by a successful step remains persisted even when
   the overall job is partial or failed.

## Overall Outcome

`DependencyExecutionRecord 1.0` uses `ALL_SUCCEEDED`, `PARTIAL_RESULTS`,
`ALL_FAILED`, or `VALIDATION_ABORTED`. The existing Job status model is used:
all success becomes `completed`, some success becomes `partial_success`, and no
success or validation abort becomes `failed`.

The execution record carries succeeded, failed, blocked, and not-started
counts plus retained artifact IDs. No automatic per-step retry, parallel
scheduler, failure policy language, or dynamic replanning is added.
