# Phase 10F-15 Production Renderer Implementation

- Atoms are grouped deterministically by species/color and rendered by one `THREE.InstancedMesh` per group.
- Bonds use one bounded `LineSegments` geometry and one material.
- The unit cell uses one 12-edge `LineSegments` geometry.
- Camera, OrbitControls, reset, pan, rotate, zoom, cell toggle, and bond toggle remain deterministic.
- Metrics expose counts, instanced meshes, draw calls, geometries, materials, triangles, lines, initialization time, and first-frame time.
- The Three engine remains dynamically imported only after the Renderer tab opens.
- Chunk timeout/rejection has a typed fallback and retry action.
- Unsupported, invalid, initialization failure, and context loss preserve JSON access and backend job success.
- Responsive controls, DPR cap, touch action, textual summary, species legend, live status, and accessible labels are implemented.
