# Viewer Schema Migration Decision

| Migration | Decision | Reason |
| --- | --- | --- |
| Phase 10D to canonical v1 | unsafe | Shapes and semantics do not preserve the canonical scene contract. |
| Canonical v1 to v2 | unsafe | Periodic endpoint images and exact v2 capabilities are absent. |
| Phase 10D to v2 | unsafe | Both canonical structure and periodic topology information are missing. |
| Manifest v1 to v2 | unsafe | A v2 manifest must describe a regenerated, validated v2 scene. |

The deterministic converter is `NOT_IMPLEMENTED_BY_DESIGN`. Assigning zero
offsets would only encode same-cell edges and must not be presented as complete
periodic topology. Regeneration from the retained structure resource is the
only approved path.
