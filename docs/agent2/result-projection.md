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

## Production lifecycle closure

After the Phase 4 supervisor commits `ExecutionSummary` and `RESULT_PENDING`,
the worker runtime publishes an identity-only RQ wakeup:

```json
{"turn_id": "..."}
```

The result worker reloads the turn, plans, exact source versions, ToolCalls
and committed Artifact payloads from PostgreSQL/MinIO. It then persists one
immutable snapshot and advances the turn to `RESULT_READY`. Duplicate tasks,
worker restarts and a queue publication failure are recoverable through the
same `turn_id`; a failed publication does not change execution authority.
The authorized `POST .../project-result` endpoint remains a recovery/manual
retry hook only.

The nine canonical production contracts are specialized by typed adapters:

| Capability family | Current production contract | Numeric policy |
| --- | --- | --- |
| RDF | `phase10e7.rdf.v1` | Declared summary fields only; curves remain structured |
| Theoretical XRD | `phase10e4.xrd_pattern.v1` | Peak summary/wavelength only when present |
| XRD comparison | `phase10n3.experimental_xrd_comparison.v1` | Match/coverage/shift summaries with locators |
| ML regression | `phase10k3.materials_ml_regression.v1` | Evaluation metrics and task identity |
| Trajectory MSD/diffusion | `phase10n4.trajectory_*` | Curve/table plus declared fit summaries |
| Phonon band/DOS | `phase10h*.*_summary.v1` | Frequency/mode summaries; no eigenvector inference |

Every quantitative fact carries a committed Artifact ID and resolvable JSON
locator. Image-only, filename-only and prose-only inputs never create numeric
facts. The full closure matrix and fresh-process evidence are recorded in
`AGENT2_PHASE5_RESULTS.md`.
