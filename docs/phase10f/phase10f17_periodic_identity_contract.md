# Periodic Identity Contract

`PeriodicSiteRef = { siteIndex, imageOffset }` is the only displayed-atom identity. `siteIndex` is canonical and `imageOffset` is a bounded integer lattice translation. Renderer instance ids and Three.js object ids are implementation details.

Instanced meshes store an immutable instance-to-ref array. Selection, highlights, snapshots, inspector fields, measurements, and screen projections carry the full ref. Scene and supercell changes rebuild mappings and clear unfinished selection state.
