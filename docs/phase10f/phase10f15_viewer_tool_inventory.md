# Phase 10F-15 Viewer Tool Inventory

| Tool | Current state | Schema/output | Runtime | Renderer | Decision |
|---|---|---|---|---|---|
| `structure.viewer_scene` | active | canonical `phase10f8.viewer_scene.v1` | canonical adapter | client renderer eligible | retain explicit JSON export |
| `structure.viewer_scene_metadata` | active legacy | `phase10d1.viewer_scene.v1` | Phase 10D adapter | JSON-only | retained, direct-purpose |
| `structure.viewer_export_package` | active legacy | Phase 10D scene/manifest | Phase 10D adapter | JSON-only | retained, direct-purpose |
| `structure.structure_3d` | active | static Plotly artifacts | pymatviz adapter | Plotly only | retain separate static tool |
| `structure.viewer_3d` | formal active | canonical scene/manifest/summary/recipe | canonical adapter subclass | production-minimal Three.js | selected formal viewer |

The previous `structure.viewer_3d` adapter emitted MatterViz HTML or fallback HTML. Phase 10F-15 replaces that active behavior because executable HTML conflicts with the canonical inert-artifact boundary.
