# Phase 10F-12 Viewer Scene Minimal Adapter Implementation

## Result

Phase 10F-12 implements the minimal, renderer-free `structure.viewer_scene` adapter.
The adapter converts one periodic `pymatgen.Structure` input into canonical
`viewer_scene.v1` inert JSON artifacts:

- `viewer_scene.json`
- `viewer_scene_manifest.json`
- `summary.md`
- `recipe.json`

This phase does not implement full `structure.viewer_3d`, WebGL, Three.js,
canvas/iframe rendering, renderer bundles, phonon, Brillouin-zone 3D,
trajectory viewing, notebook execution, external API access, or real LLM
execution.

## Implementation

- Adapter: `StructureViewerSceneAdapter`
- Tool id: `structure.viewer_scene`
- Domain: `structure`
- Registry manifest: `tool_registry/platform_builtin_manifest.yaml`
- Canonical scene schema: `phase10f8.viewer_scene.v1`
- Canonical manifest schema: `phase10f9.viewer_scene_manifest.v1`
- Contract validator: `mdi_artifact_core.validate_viewer_scene`
- Manifest validator: `mdi_artifact_core.validate_viewer_scene_manifest`

The adapter reuses the existing lightweight structure parser in
`platform_builtin/structure.py` and accepts exactly one periodic structure. It
rejects multi-structure inputs rather than silently selecting one.

## Params

The registered params schema is strict and rejects unknown keys. Supported
params are:

- `include_bonds`
- `bond_cutoff_angstrom`
- `max_sites`
- `max_bonds`
- `coordinate_basis`
- `include_cartesian_positions`
- `include_fractional_positions`
- `cell_expansion`
- `style_preset`
- `camera_preset`

Hard caps are aligned with the Phase 10F contract:

- `max_sites <= 256`
- `max_bonds <= 2048`
- `max_species <= 32`
- `cell_expansion == [1, 1, 1]`
- `max_scene_json_bytes <= 1000000`

## Bond Policy

Bonds are optional and non-authoritative. When enabled, the adapter emits
bounded distance-cutoff candidates with policy
`distance_cutoff_non_authoritative`. It does not claim bond order, chemical
environment classification, CrystalNN behavior, or advanced local environment
analysis.

## Validation

`viewer_scene.json` and `viewer_scene_manifest.json` are validated before
export. If canonical validation fails, the adapter raises a typed
`TOOL_CONTRACT_INVALID` error and does not write a successful artifact set.

## Runtime Integration

The adapter is registered in Tool Registry and can run through:

- Tool Registry lookup
- strict params validation
- `execute_tool_request`
- `PlanValidator`
- `QueueWorkerRuntime`
- persisted planner job execution tests

Mock Planner routing includes only explicit inert viewer-scene JSON prompts.
Full interactive viewer, WebGL, Three.js, Brillouin-zone, phonon, RDF, XRD, and
coordination prompts are not routed to `structure.viewer_scene`.
