# Phase 10F-7 Viewer Input and Size Caps

## 1. Suggested Initial Caps

```json
{
  "max_sites": 256,
  "max_bonds": 2048,
  "max_unit_cell_edges": 12,
  "max_species": 32,
  "max_cell_expansion": [1, 1, 1],
  "max_scene_json_bytes": 1000000
}
```

## 2. Input Support Assessment

- CIF: supported by existing structure parsing paths and suitable for small crystalline structures.
- POSCAR: supported by existing structure parsing paths and suitable for bounded crystalline inputs.
- Structure JSON: useful for deterministic internal fixtures and future direct-uploadable scene contract tests.
- Notebook or script extraction: not allowed.
- External API inputs: not allowed.

## 3. Periodic and Non-Periodic Policy

- First artifact-contract phase should support structures already accepted by the existing parser.
- Periodic crystalline structures should include unit-cell vectors and PBC.
- Non-periodic inputs require explicit policy before renderer work because unit-cell display and camera framing differ.
- Missing or invalid lattice data must produce typed errors or stable warnings according to existing adapter conventions.

## 4. Supercell Expansion Policy

- Default expansion is `[1, 1, 1]`.
- No automatic supercell expansion beyond `[1, 1, 1]` in the first implementation scope.
- Any future expansion must have explicit caps and deterministic ordering.

## 5. Bond Inference Policy

- Prefer no bonds or existing safe helper output for the first contract.
- If bonds are included, cap at `max_bonds`, sort deterministically, and record truncation warnings.
- Do not add advanced local environment classification, VoronoiNN, or CrystalNN in the viewer scope.

## 6. Element Style Policy

- Element colors and radii must come from a deterministic local table or existing helper.
- Missing element style should use stable fallback values.
- Style metadata is data only and must not contain callbacks or remote assets.

## 7. Unit Cell Policy

- Unit-cell vectors should be serialized in Cartesian angstrom coordinates.
- Unit-cell edges should be deterministic and capped at `max_unit_cell_edges`.
- Invalid or degenerate cells should be rejected or warned before renderer use.

## 8. Warnings and Determinism

- Warnings must use stable codes and ordering.
- Sites sort by site index.
- Bonds sort by endpoint indices and image/offset metadata if present.
- Numeric values should be rounded to fixed precision set by the contract phase.

## 9. Recommended First Implementation Scope

Small `viewer_scene.json` only; no interactive renderer, no WebGL, no Three.js, no automatic supercell beyond `[1, 1, 1]`, and optional bonds only if an existing safe helper is reused.
