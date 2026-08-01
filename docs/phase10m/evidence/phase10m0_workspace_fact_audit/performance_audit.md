# Current Performance and Loading Audit

These are development audit observations, not production capacity claims.

- Current Next production build: root route 144 kB, first-load JS 247 kB,
  shared first-load JS 103 kB.
- Current PlannerWorkbench loads six independent Job read slices after
  submission; there is no atomic metadata-first Workspace snapshot.
- Current browser replays completed without document-level horizontal overflow.
- L4 per-case elapsed values are retained in
  `browser_interpretation_current/browser_matrix.json`; they include local
  Next/render/test overhead and are not service latency.
- Existing trajectory, WebGL, volumetric, artifact, evidence, and planning caps
  remain unchanged.
- Current UI does not restore a large historical Workspace because the route
  and persistence do not exist.

The sealed future targets are in
`docs/phase10m/phase10m0_responsive_accessibility_performance_security.md`.
They require metadata-first loading, active-panel lazy payload, four concurrent
requests, cancellation, ETag/source-hash invalidation, explicit WebGL cleanup,
and measured 20-switch lifecycle evidence.
