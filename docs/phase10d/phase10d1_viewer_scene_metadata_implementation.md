# Phase 10D-1 Viewer Scene Metadata / Export Package Implementation

## 1. Scope

Implemented:

- `structure.viewer_scene_metadata`
- `structure.viewer_export_package`

Not implemented:

- Full interactive `structure.viewer_3d`
- WebGL / Three.js renderer
- Brillouin-zone 3D
- XRD
- RDF
- coordination histogram
- phonon bands / DOS
- notebook extraction
- script execution

Optional `structure.viewer_3d_contract` was not implemented in this phase. The contract is represented by the `viewer_scene.json` schema and can become a separate schema-only tool later if needed.

## 2. Tool IDs

### `structure.viewer_scene_metadata`

Creates a static, non-executable scene metadata artifact for future structure viewer rendering.

Outputs:

- `viewer_scene.json`
- `summary.md`
- `recipe.json`

### `structure.viewer_export_package`

Creates a static export package contract around the scene metadata. The package does not include a renderer.

Outputs:

- `viewer_scene.json`
- `viewer_assets_manifest.json`
- `summary.md`
- `recipe.json`

## 3. Artifact Contract

### `viewer_scene.json`

Required semantics:

- `schema_version: phase10d1.viewer_scene.v1`
- `artifactType: structure.viewer_scene_metadata`
- `tool_id`
- source metadata
- structure count and structure records
- lattice matrix and lattice parameters
- atom records with stable indexes, labels, elements, coordinates, display radius, and display color
- deterministic inferred bonds or an explicit warning when bonds are skipped
- display metadata
- camera metadata
- style metadata
- limits and truncation metadata
- security flags showing no JavaScript and no external URLs

### `viewer_assets_manifest.json`

Required semantics:

- `schema_version: phase10d1.viewer_assets_manifest.v1`
- `artifactType: structure.viewer_export_package`
- static package metadata
- `entry_artifact: viewer_scene.json`
- artifact list with media types and required flags
- renderer metadata with `included: false`
- security flags showing no JavaScript, no external URLs, and no artifact-supplied JavaScript
- limits and warnings

### `summary.md`

Human-readable report covering:

- input source
- parser
- formula
- site count
- output artifacts
- display settings
- limits
- warnings
- security boundary

### `recipe.json`

Reproducibility record covering:

- schema version
- tool id
- inputs and input hashes
- normalized params
- deterministic execution steps
- dependency versions
- artifact list

## 4. Params

`structure.viewer_scene_metadata` supports strict params:

- `inferBonds` / `infer_bonds`
- `bondTolerance` / `bond_tolerance`
- `maxSites` / `max_sites`
- `maxBonds` / `max_bonds`
- `includeCartCoords` / `include_cart_coords`
- `includeFracCoords` / `include_frac_coords`
- `stylePreset` / `style_preset`
- `cameraPreset` / `camera_preset`

`structure.viewer_export_package` supports the same scene params plus:

- `includeScene` / `include_scene`
- `includeManifest` / `include_manifest`
- `includeSummary` / `include_summary`
- `includeRecipe` / `include_recipe`
- `maxPackageBytes` / `max_package_bytes`

The implementation preserves project convention by normalizing params to camelCase internally while accepting the snake_case names requested by the Phase 10D-1 contract.

## 5. Security Boundary

- No artifact JavaScript is generated.
- No renderer bundle is generated.
- No HTML viewer is generated.
- No external URL is embedded.
- No WebGL / Three.js / MatterViz runtime is introduced.
- No arbitrary local path is read.
- No notebook or script is executed.
- No real LLM is used.

## 6. Planner Routing

Mock Planner routes:

- viewer scene metadata prompts -> `structure.viewer_scene_metadata`
- viewer export package prompts -> `structure.viewer_export_package`

Mock Planner does not route full interactive 3D, WebGL, Brillouin-zone, XRD, RDF, coordination histogram, or phonon prompts to the new Phase 10D-1 tools.

## 7. Tests

Added tests cover:

- viewer scene metadata artifact contract
- deterministic bond inference
- bond skipping
- site truncation warnings
- export package manifest contract
- no JavaScript / no external URL assertions
- strict Tool Registry params schemas
- Mock Planner routing
- deferred prompt boundaries
- persisted plan -> job -> ToolCall -> artifact execution
- existing Phase 10C lightweight structure regression

## 8. Evidence Policy

Phase 10D-1 includes lightweight adapter evidence only under:

```text
docs/phase10d/adapter_evidence/
```

Evidence level:

```text
Tool Registry + Adapter execution only
```

Browser/API evidence is deferred to Phase 10D-2.

## 9. Deferred Scope

- full `structure.viewer_3d`
- Brillouin-zone 3D
- XRD
- RDF
- coordination histogram
- phonon
- browser/API evidence
- notebook/script extraction
