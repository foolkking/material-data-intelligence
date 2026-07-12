# Phase 10F-16 Atom Picking Design

Three.js `Raycaster` intersects visible atom `InstancedMesh` objects only. Each
mesh stores a deterministic application-owned `instanceId -> canonical siteIndex`
array. A pointer movement above 5 CSS pixels is an orbit drag and does not select.
Empty clicks clear selection. Scene replacement rebuilds the mapping and clears
selection. Four reusable wireframe overlays mark A/B/C/D; they and all pointer
listeners/materials are disposed with the engine.
