# Agent 2.0 Phase 4 State Flow

```text
PLAN_READY
  -> QUEUED
      -> RUNNING
          -> RESULT_PENDING   (SUCCESS or PARTIAL)
          -> FAILED           (no usable scientific execution)
          -> CANCELING
              -> CANCELED     (runtime confirmed)
              -> RESULT_PENDING (execution won cancellation race)

QUEUED
  -> RESULT_PENDING           (fast terminal Job recovery)
  -> FAILED
  -> CANCELING -> CANCELED / RESULT_PENDING
```

`PLAN_READY` means a validated Plan exists but no Job. `QUEUED` means one
existing Job is attached; queue publication alone never means `RUNNING`.
`RUNNING` requires a real Job running state. Fast Jobs may move directly from
`QUEUED` to a terminal projection without inventing a RUNNING timestamp.

`RESULT_PENDING` requires a terminal successful/partial Job and immutable
ExecutionSummary. It is not a completed research answer: ScientificResult
projection, interpretation, grounding, and assistant final response remain
absent. A cancel request at this state is rejected because execution is already
terminal. Phase 5 alone may advance result projection.
