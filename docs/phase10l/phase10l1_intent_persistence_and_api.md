# Phase 10L-1 Intent Persistence and API

## Persistence

Alembic revision `0003_phase10l1_intents` adds immutable
`analysis_intents` and `analysis_intent_executions` tables. The former stores
the exact validated contract, hash, outcome, parent/revision state, provider,
model, prompt version, project/dataset/Profile binding, and timestamps. The
latter associates one READY intent with its existing plan and job outside
`AnalysisPlan 0.1`.

In-memory and SQLAlchemy repositories implement the same idempotent save,
immutable association, get, and job reverse-lookup behavior. Production schema
changes use Alembic; `metadata.create_all` is test-only.

## API

* `POST /planner/intents`: build, validate, and persist an intent.
* `GET /planner/intents/{intent_id}`: return a persisted intent.
* `POST /planner/intents/{intent_id}/clarification`: validate answers and save
  an immutable revision.
* `POST /planner/jobs`: additively activates the Intent Gate when
  `intentSchemaVersion=1.0` or `intentId` is supplied.

Non-READY requests return typed intent state before plan/job persistence or
enqueue. READY requests pass the preserved raw goal to the unchanged existing
Planner and store the external intent-plan-job association. Job detail includes
the additive intent binding. Legacy callers that omit Intent fields retain the
historical Planner API behavior; the canonical frontend now opts into v1.

Errors are bounded and user-safe. Stale Profile/resource, schema, provider,
clarification, and identity failures do not expose stack traces or provider raw
responses.
