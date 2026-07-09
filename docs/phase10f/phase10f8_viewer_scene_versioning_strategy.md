# Phase 10F-8 Viewer Scene Versioning Strategy

## 1. Version Identifiers

The v1 contract should use:

- `kind: viewer_scene`
- `version: viewer_scene.v1`
- `schema_version: phase10f8.viewer_scene.v1`

The manifest contract should use:

- `kind: viewer_scene_manifest`
- `version: viewer_scene_manifest.v1`
- `schema_version: phase10f8.viewer_scene_manifest.v1`

## 2. Compatibility Policy

| Change Type | Policy |
|---|---|
| Add optional preview-only metadata | forward-compatible |
| Add optional renderer-facing declarative field | forward-compatible if ignored safely by older consumers |
| Add required top-level field | new schema version required |
| Change coordinate basis semantics | new schema version required |
| Change security defaults | new schema version and security review required |
| Allow external resources | not allowed in v1; future version requires explicit approval |
| Add renderer-required artifact behavior | not allowed in v1; future version requires explicit approval |

## 3. Strict Rejection vs Warning

Strict rejection is required for:

- invalid or missing required identity fields;
- non-finite required numeric fields;
- executable/script-like fields;
- external URLs or remote assets;
- renderer-required flags in JSON-only phase;
- payloads beyond size caps.

Warnings are acceptable for:

- optional bonds omitted;
- style hints ignored;
- unknown optional metadata fields that do not affect security;
- deterministic truncation when explicitly recorded and approved by contract.

## 4. Renderer Fallback Behavior

A future renderer must:

- refuse unsupported major versions;
- display a static JSON fallback when renderer-facing fields are missing but preview fields are valid;
- refuse artifacts that require external resources;
- refuse artifacts that mark `renderer_required: true` unless an approved renderer phase defines that behavior;
- avoid guessing coordinate semantics when `coordinate_basis` is missing or unsupported.

## 5. Future `viewer_scene.v2`

`viewer_scene.v2` may be considered only after v1 JSON-only evidence is stable. Potential v2 topics include richer materials, multiple structures, larger scene paging, explicit animation metadata, or renderer-specific camera states. Any v2 migration must preserve the no-JS/no-external-URL rule unless a separate security review explicitly changes that boundary.

## 6. Disallowed v1 Extensions

The following remain out of v1:

- compressed artifact payloads;
- multi-structure scenes;
- renderer bundles;
- remote textures or model assets;
- WebGL/Three.js-specific shader or material code;
- phonon trajectories;
- Brillouin-zone geometry;
- advanced local environment classifier output.
