# Phase 10F-15 Tool Consolidation Decision

## Selected Strategy

Promote and safely replace the existing `structure.viewer_3d` behavior. Its adapter now reuses the canonical `StructureViewerSceneAdapter` generation, validation, and artifact export path with formal tool identity.

Natural viewer prompts route to `structure.viewer_3d`. Explicit `viewer_scene` JSON prompts continue to route to `structure.viewer_scene`. Legacy metadata/export prompts retain their old explicit routes. Trajectory, phonon, Brillouin-zone, volumetric, editing, XRD, RDF, and coordination prompts do not route to the minimal viewer.

No duplicate tool id exists. No HTML renderer artifact remains in the formal viewer artifact declaration.
