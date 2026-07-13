# Phase 10F-27 structure.viewer_3d API Evidence

The evidence generator executes real local `/planner/jobs` router functions,
persists the AnalysisPlan, invokes QueueWorkerRuntime and
`StructureViewer3DAdapter`, lists artifacts, reloads their content, and runs the
canonical scene and manifest validators.

Cases include minimal Si, multi-species NaCl, warning/cap degradation, disabled
bonds, invalid multi-structure input, orthogonal boundary topology, triclinic
boundary topology, and self-periodic topology. Registry/catalog snapshots and
SHA-256 hashes are generated from the same run. Synthetic fixtures are not
used for successful product evidence and no real LLM is invoked.

Command:

```text
node apps/web/test/viewer-scene-formal-product-browser-evidence.mjs
```

The committed captures are under
`evidence/phase10f27_structure_viewer_3d_product/`.

Local result: eight live cases completed or failed as expected; every completed
scene and manifest passed its canonical validator. The formal registry/catalog
entry was unique and owned by `platform_builtin_manifest.yaml`.
