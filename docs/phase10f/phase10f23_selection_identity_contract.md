# Selection Identity Contract

- Atom key: application-generated `siteIndex:imageX:imageY:imageZ`.
- Bond key: exact `RenderBond.id` from validated canonical topology or bounded
  deterministic supercell replication.
- Instanced atom mapping is immutable `instanceId -> PeriodicSiteRef`.
- Shared line mapping is deterministic `segment index -> bond id`.
- Duplicate atom refs toggle off; bond endpoints retain emitted order.
- Caps are inspect 1, distance 2, angle 3, and dihedral 4.
- Scene/supercell changes, context loss, clear, and mode changes remove stale
  selections and bond highlights.
