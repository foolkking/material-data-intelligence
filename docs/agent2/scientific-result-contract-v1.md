# Scientific Result Contract v1

`ScientificResultBundle` is a typed projection contract for existing
Job/ToolCall/Artifact/Evidence data. `ScientificResultSnapshot` is a
deterministic, historical projection cache; it is not a new source-of-truth
authority.

## Bundle

Every bundle has `schema_version: "1.0"`, result/project/session/turn
identity, a research question, exact source/output object references, result
items, facts, figures, tables, evidence, methods, limitations, warnings,
provenance, and `projection_version`.

`execution_status` (`SUCCESS`, `PARTIAL`, `FAILED`) and `relevance_status`
(`CURRENT`, `STALE`, `SOURCE_MISSING`, `INVALIDATED`) are independent. A fact
must have at least one locator (ToolCall, Artifact, artifact locator, or
ScientificObjectRef); fact and result-item IDs are unique and references are
validated.

## Snapshot persistence

`ScientificResultSnapshotService.persist_snapshot()` verifies Turn scope and
re-authorizes every object/version reference in source, output, result items,
and fact locators before storing the JSON bundle. Identity is
`(research_turn_id, projection_version, source_fingerprint)`, making replay
idempotent. `get_latest_for_turn()` and `list_for_turn()` return validated
bundles.

## Phase 1 boundary

The schema, validation, persistence foundation, and fixture projector
registry are implemented. Production projection from all existing tools,
grounding validation, interpretation, assistant scientific responses, and
Report composition remain later-phase work.
