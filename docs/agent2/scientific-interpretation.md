# Agent 2.0 Scientific Interpretation

Phase 6 turns a persisted `RESULT_READY` ScientificResultBundle into a
grounded assistant message. The interpreter never reads raw Artifact payloads,
executes tools, changes parameters, or becomes a source of scientific facts.

## Input boundary

`InterpreterInputAssembler` creates a bounded `InterpretationInputEnvelope`
from the immutable result bundle. It includes the effective relevance status,
result items, referenced facts and evidence, compact figure/table metadata,
methods, limitations, warnings, and the research question. Raw files, image
bytes, large arrays, credentials, prompts, and provider transcripts are not
included. Every bounded collection has a fixed maximum; truncated identities
are listed in `omitted_supporting_items` rather than disappearing silently.

## Structured output

The provider must return `ScientificInterpretationOutput` contract `1.0`:
title, answer lead, primary/supporting findings, result references,
limitations, and follow-up proposals. A finding is not accepted without a
fact or evidence reference. The prompt version is frozen as
`scientific-interpreter/1.0`.

## Grounding gate

`EvidenceReferenceValidator` resolves every fact, evidence, and result-item
reference against the current bundle. `QuantitativeClaimValidator` checks
numeric tokens against referenced machine-readable fact values and preserves
units without conversion. `answer_lead` cannot introduce an unsupported
number. Status validation prevents a PARTIAL result from being described as a
complete analysis. Invalid schema or grounding output receives at most one
bounded repair; a second failure is persisted as a typed interpretation
failure and never becomes a message.

## Lifecycle and persistence

Normal analysis follows:

```text
RESULT_READY -> INTERPRETING -> COMPLETED / PARTIAL
```

Phase 2 `INTERPRET_RESULT` turns enter the same interpretation service from
`ORCHESTRATING` and reuse an authorized existing snapshot without creating a
plan, Job, ToolCall, Artifact, or new result snapshot. Grounded output and the
rendered message are stored immutably in `agent2_scientific_interpretations`
and the existing ResearchMessage table. Duplicate delivery returns the stored
interpretation; stale `INTERPRETING` claims can be recovered by the
reconciler. Interpretation identity is unique per ResearchTurn, not per source
snapshot, so separate follow-up turns may independently interpret the same
authorized historical Result.

Phase 5 publishes only `{ "turn_id": "..." }` after committing
`RESULT_READY`. A fresh RQ worker reloads PostgreSQL authority and calls the
existing structured provider adapter outside a database transaction. Queue
failure leaves `RESULT_READY` readable and republishable. The authorized
`POST /api/research/turns/{turn_id}/interpret` recovery hook also only
republishes the identity and returns `202`; it never waits for the provider in
the HTTP transaction.

## Assistant response

`AssistantResponseProjector` deterministically renders the validated output,
injecting mandatory PARTIAL/STALE/SOURCE_MISSING/INVALIDATED notices. It does
not expose fact IDs, artifact IDs, Job/ToolCall IDs, provider metadata, or
hidden reasoning. Final messages are created exactly once and remain attached
to the ResearchTurn; Phase 6 does not create reports, interpretations for
unreferenced history, or new scientific computation.
