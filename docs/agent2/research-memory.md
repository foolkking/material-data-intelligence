# Agent 2.0 Research Memory v1

Phase 7 introduces a small, auditable ResearchSession memory projection. It is
not a scientific-fact store and it is not a provider transcript.

## Authorities and boundaries

- PostgreSQL `research_session_states` is the mutable session projection.
- `research_session_context_items` records who/which user message requested a
  session constraint or pin.
- `research_context_snapshots` remain immutable per-turn evidence and are never
  rewritten when the session projection changes.
- Candidate assembly is deterministic and project-authorized before the
  Orchestrator receives it. Provider payloads use opaque `obj_N`, `result_N`,
  and `finding_N` keys; database IDs are excluded from compact provider views.

## Context and reuse

Candidate priority is explicit reference, current UI selection, current scope,
previous-turn result, pinned context, recent context, then bounded
long-session retrieval. Historical result candidates are capped and carry the
original relevance/staleness status and exact source versions. A referenced
result is interpreted without creating a Plan, Job, ToolCall, Artifact, or new
ResultSnapshot.

Explicit parameter changes are represented by `CONTINUE_ANALYSIS`; the old
Turn, Plan, Job, and Result remain immutable and the new Turn points to the
continuation source.

## Session mutations

Only explicit session language (for example “后面这个 Session 都用 cutoff
8 Å”) creates a `SESSION_CONSTRAINT`. “这次 cutoff 用 8 Å” remains turn
scoped. Constraint replacement and clearing deactivate the previous item and
increment the state version. Pin/unpin operations are project-authorized and
idempotent.

## Budget and retrieval

The compiler keeps current request data, constraints, pinned/referenced
results, and exact identities ahead of low-value prose. It uses a bounded
recent-message/result view and a deterministic session query (maximum 500
prior turns / 16 result candidates); no vector database or semantic SaaS is
required in v1.

## Deliberate non-goals

There is no global memory, chain-of-thought persistence, report composer, data
management mutation workflow, or new scientific computation in Phase 7.
