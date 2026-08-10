# Phase 12-1 Design System 2.0

`DESIGN_SYSTEM_VERSION = 2.0` is a frontend presentation version, not a
scientific contract, Artifact identity, Plan hash, or Workspace authority.

The system has five layers:

1. Primitive tokens in `apps/web/app/globals.css` for palette, space, radius,
   border, elevation, duration, z-index, breakpoints and control sizes.
2. Semantic tokens for background/surface/text/accent/focus/selection/overlay.
3. Presentation-only semantic status tokens.
4. Shared native-control, panel, table, overlay and status primitives.
5. Product and specialized scientific surfaces, which continue to own their
   scientific payloads, category colors and interactions.

The legacy aliases remain temporary compatibility mappings. They are tracked in
the evidence migration matrix and do not create a second semantic authority.
`StatusLabel` is the shared, text-bearing status primitive; callers retain the
exact persisted domain state and select only a visual variant.

No UI action, route, Planner/Workspace workflow, scientific value, scientific
identity, unit, Registry entry, Profile fact, API, backend behavior or data model
is changed by this foundation.
