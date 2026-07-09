# Phase 10F-8 Viewer Scene Artifact Contract Planning

## 1. Scope

- planned: inert `viewer_scene` artifact identity, JSON shape, manifest contract, validation contract, security boundary, browser JSON-only evidence model, versioning strategy, and Phase 10F-9 next scope.
- not implemented: `structure.viewer_3d`, WebGL renderer, Three.js integration, renderer bundle, frontend viewer component, adapter, planner routing, Tool Registry runtime behavior, phonon, Brillouin-zone 3D, advanced local environment classification, notebooks, external scripts, external APIs, or artifact JavaScript.

## 2. Baseline

- Phase 10F-7 HEAD: `35bd2e9fd17c85bf942d73b4fd524ff49e587cb8`
- Phase 10F-7 commit: `35bd2e9 Plan advanced structure viewer readiness`
- current HEAD before: `35bd2e9fd17c85bf942d73b4fd524ff49e587cb8`
- branch: `master`
- git status before: clean

## 3. Contract Goal

Phase 10F-8 fixes a planning-level contract for future `viewer_scene` artifacts. The contract is intentionally renderer-neutral:

- `viewer_scene.json` is inert JSON data.
- JSON-only artifact preview is the first intended consumer.
- Renderer implementation is deferred.
- Future renderer work must treat the artifact as untrusted data and must not execute artifact-provided content.

The contract builds on Phase 10D static scene metadata and Phase 10D-3 static preview evidence, but it does not change existing `structure.viewer_scene_metadata` behavior or activate historical `structure.viewer_3d` inventory.

## 4. Contract Documents

| Contract Area | Document | Decision |
|---|---|---|
| Artifact identity and JSON shape | `phase10f8_viewer_scene_json_contract.md` | `READY` for contract draft |
| Manifest contract | `phase10f8_viewer_scene_manifest_contract.md` | `READY` for contract draft |
| Validation contract | `phase10f8_viewer_scene_validation_contract.md` | `READY` for contract draft |
| Security boundary | `phase10f8_viewer_scene_security_contract.md` | `READY` for JSON-only phase |
| Browser evidence | `phase10f8_viewer_scene_browser_evidence_contract.md` | `READY` for JSON-only preview planning |
| Compatibility / migration | `phase10f8_viewer_scene_versioning_strategy.md` | `READY` for v1 draft |
| Readiness matrix | `phase10f8_viewer_scene_contract_readiness_matrix.md` | renderer remains `NOT_READY` |

## 5. Contract Identity

- artifact kind: `viewer_scene`
- contract version: `viewer_scene.v1`
- schema version: `phase10f8.viewer_scene.v1`
- intended first consumer: static JSON artifact preview
- renderer consumer: deferred and explicitly not required for Phase 10F-8
- executable content: prohibited
- external resource references: prohibited

## 6. Readiness Summary

- viewer_scene artifact contract planning: `READY`
- JSON-only preview planning: `READY`
- renderer handoff: `PARTIAL_READY`
- renderer implementation: `NOT_READY`
- full `structure.viewer_3d` implementation: `NOT_READY`

## 7. Boundary

Phase 10F-8 does not create a new adapter, does not register a new tool, does not alter planner routing, and does not introduce a renderer dependency. It only defines the contract work needed before any future implementation phase.

## 8. Conclusion

PASS. Viewer scene artifact contract planning is complete, with JSON-only preview planning ready for Phase 10F-9 and full renderer/full viewer implementation explicitly not approved.
