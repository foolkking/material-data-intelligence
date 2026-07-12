# Viewer Schema Deprecation Policy

Phase 10D artifacts remain listable, inspectable, and available as inert JSON.
They are rejected before renderer mapping with
`VIEWER_SCENE_RENDERER_SCHEMA_UNSUPPORTED`. Canonical v1 remains replayable
under its established same-cell boundary and emits
`VIEWER_SCENE_LEGACY_SAME_CELL_TOPOLOGY`.

Removal requires an artifact retention decision, fixture replacement, direct
legacy tool retirement, and a user-visible regeneration window. Deprecation is
not a validation or security failure, and historical payloads are not rewritten.
