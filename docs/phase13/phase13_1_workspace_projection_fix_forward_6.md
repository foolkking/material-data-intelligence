# Phase 13-1 Integration Fix-Forward #6

## Scope

This fix-forward closes `P13-RSE1-001`, `P13-R5-001`, and `P13-R5-002`. It keeps
`MAX_PANELS_PER_WORKSPACE = 32` and changes only Workspace projection cardinality:
persisted Artifacts remain exact scientific authorities, while supporting Artifacts
under one Job-bound logical Results surface are reached through the existing Artifact
Gallery and typed renderers.

The authorized typed phonon entry remains narrow: explicit `PhononBand` and
`PhononDos` imports reuse the existing contracts and durable Dataset/Profile resource
pipeline. Generic phonon YAML/JSON remains `MAPPING_ONLY`. No scientific algorithm,
Tool, Adapter, Artifact family, schema version, migration, or validation promotion is
introduced.

## Closure Evidence

The independent evidence root is
`evidence/phase13_1_workspace_projection_fix_forward_6/`. Fresh Demo 4 and Demo 5
states are recorded there. Demo 5 persisted 27 Artifacts and projects 7 Workspace
panels: six structural panels plus one Job-bound Results/Gallery surface. All 27
Artifacts remain checksum- and lineage-addressable; no payload is copied or dropped.

The previous one-panel-per-Artifact projection produced 33 candidates and correctly
rejected the Workspace at the fixed cap. The new projection is generic for Jobs with
many supporting Artifacts and does not route on Demo, phonon, filename, MIME, array
position, timestamp, latest, nearest, or fuzzy labels.

## Authority State

Current Fact Model: `92d8295c7d78467d8ce021dc8033a58326219372a5d8fa87c93377ed1275953a`.
Current Scope Baseline: `bb885aa4e020349011c39164a883107c8ffed3d5d43604594a76f7d5a18705ba`.
Phase 12 Product Baseline remains
`29936236efe74a82ad97507385839aa4f5692d26b496292af3172940647973d4`.

Attempt 6 is not executed or queued. Its reviewer handoff is retained as
`Phase13_2Attempt6RealUserE2ERerunHandoff`.
