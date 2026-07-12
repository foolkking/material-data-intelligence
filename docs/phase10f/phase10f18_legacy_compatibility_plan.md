# Legacy Compatibility Plan

`phase10f8.viewer_scene.v1` remains validator-compatible. Its bonds are interpreted as `[0,0,0] -> [0,0,0]` only and receive `VIEWER_SCENE_LEGACY_SAME_CELL_TOPOLOGY` in the renderer mapper. Phase 10D artifacts remain JSON-only with rerun guidance.

There is no mutation or automatic migration of historical artifacts. Both formal tools now emit v2; planner identities and backend job semantics are unchanged.
