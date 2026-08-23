# Agent 2.0 Phase 5 Result Projection

Phase 5 converts committed Phase 4 execution facts into an immutable
`ScientificResultBundle` snapshot. It does not execute tools, call an LLM, or
write an assistant final response.

## Authority and lifecycle

`Job`, `ToolCall`, `Artifact`, `JobEvent`, and exact `ScientificObjectVersion`
rows remain the source of truth. The projector reads those rows, validates
their project scope, and persists into the existing
`scientific_result_snapshots` table. A successful or partial projection moves
`ResearchTurn` from `RESULT_PENDING` to `RESULT_READY`; projection failure
leaves execution facts intact and the turn retryable.

## Deterministic projectors

The registry currently resolves the canonical families registered by Phase 3:
RDF, theoretical and comparative XRD, ML regression, trajectory MSD and
diffusion, and phonon band/DOS. Projectors consume structured committed
artifact payloads. Image-only artifacts can become figures, but never create
numeric facts. Every numeric fact carries an artifact ID and JSON locator.

## Snapshot identity

The source fingerprint canonically hashes the turn, execution summary, exact
plan identities, capability plan, source versions, tool calls, artifacts, and
projector/version identities. Timestamps, URLs, process IDs, and map ordering
are excluded. Existing snapshots are immutable; a same-version fingerprint
conflict fails closed.

## Relevance

Stored source references never upgrade. At read time, exact versions are
evaluated as `CURRENT`, `STALE`, `SOURCE_MISSING`, or `INVALIDATED` without
rewriting the stored bundle.

## API and boundaries

`GET /api/research/turns/{turn_id}/result` requires project authorization and
returns a bounded product view. `POST .../project-result` is the authorized
deterministic processing hook used by qualification tooling. `RESULT_READY`
does not imply interpretation or a final assistant answer; those remain
Phase 6 work.
