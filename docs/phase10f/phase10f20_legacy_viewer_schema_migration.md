# Phase 10F-20 Legacy Viewer Schema Migration

Phase 10F-20 makes viewer schema lifecycle policy executable without changing
the renderer, canonical periodic identity, or runtime authority. The shared
compatibility registry classifies Phase 10D as deprecated read-only, canonical
v1 as supported legacy same-cell, and v2 as current.

Current adapters and planner routes produce v2 scenes and manifest v2. Legacy
tools remain direct-execution compatibility producers so historical tests and
artifacts are not deleted, but Mock Planner no longer selects them.

No converter is implemented. Missing periodic endpoint identity cannot be
reconstructed without inference. Users must regenerate from the source
structure with `structure.viewer_3d` or `structure.viewer_scene`.
