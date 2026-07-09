# Phase 10F-7 Advanced Structure Viewer Readiness Planning

## 1. Scope

- evaluated: future advanced structure viewer readiness, inert viewer artifact contracts, renderer isolation, browser evidence requirements, input caps, and routing boundaries.
- not implemented: `structure.viewer_3d`, full interactive 3D viewer, WebGL renderer, Three.js integration, renderer bundle, browser 3D runtime, `structure.brillouin_zone_3d`, phonon bands/DOS, advanced local environment classification, or experimental fitting.

## 2. Baseline

- Phase 10F-6 commit: `918617b Close static physics fixture evidence`
- current HEAD: `918617b3a8f32c367b75c3bcd228c2062f645cc8`
- branch: `master`
- git status before: clean

## 3. Existing Capabilities

- structure parser: Phase 10C/10D/10E structure tools already consume small CIF, POSCAR, and structure-JSON-like resources through the existing registry-gated platform flow.
- lattice / sites: parsed structures preserve lattice, species, site count, positions, periodicity, and volume where required by downstream tools.
- geometry normalization: Phase 10D static scene metadata serializes deterministic site, lattice, bond, camera, and style metadata as inert JSON.
- artifact writer: existing adapters write stable JSON, Markdown summary, and recipe artifacts with explicit security metadata.
- frontend static preview: Phase 10D-3 hardened schema-aware static preview for `viewer_scene.json` and `viewer_assets_manifest.json`; it does not render a full 3D viewer.
- browser evidence tooling: Phase 10D/10E evidence used real browser-rendered artifact preview pages and can be reused for future JSON-only viewer artifact evidence.
- security scanning: current evidence uses no-JS/no-external-URL scans and records no notebook/script execution.

## 4. Advanced Viewer Candidate

- candidate tool id: `structure.viewer_3d` for a future, explicitly approved viewer path.
- current inventory note: historical registry/adapter inventory for `structure.viewer_3d` exists, but Phase 10F-7 does not activate, extend, evidence, or approve full viewer implementation.
- proposed capability: create a bounded scene artifact and, in a later phase, render it through an isolated viewer that treats the artifact as data only.
- input requirements: small direct-uploadable structure resources or an approved inert scene artifact; no notebook or script extraction.
- artifact requirements: `viewer_scene.json`, `viewer_summary.md`, and `viewer_recipe.json` should be fixed before any renderer implementation.
- renderer requirements: renderer must be separate from artifacts, dependency-reviewed, isolated, deterministic enough for screenshot evidence, and forbidden from executing artifact-provided code.
- security requirements: no artifact JS, no external URLs, no remote textures, no CDN, no dynamic imports from artifact data, no arbitrary file reads, and bounded scene size.

## 5. Readiness Assessment

- artifact contract: READY for a dedicated contract-planning/finalization phase, building on Phase 10D inert scene metadata.
- renderer isolation: NOT_READY; sandbox model, dependency policy, and renderer-data boundary are not fixed.
- frontend preview: READY for static JSON/Markdown preview only; NOT_READY for interactive renderer.
- browser evidence: READY for JSON-only artifact preview evidence; renderer evidence requires a future protocol and approval.
- dependency policy: NOT_READY for WebGL/Three.js; no new renderer dependency is approved.
- security policy: PARTIAL_READY; no-JS/no-external-URL posture exists, but renderer-specific tests and isolation are not fixed.
- performance caps: PARTIAL_READY; proposed caps exist in this phase but require contract finalization.
- planner routing: PARTIAL_READY; routing policy can be planned, but this phase does not implement routing.
- CI risk: LOW for contract/planning; MEDIUM to HIGH for renderer implementation until browser/security tests are designed.

## 6. Decision

- ready for artifact contract phase: yes. Phase 10F-8 may plan and optionally scaffold an inert `viewer_scene.json` contract.
- ready for renderer implementation: no. Renderer isolation, dependency review, browser evidence, and security tests are not fixed.
- ready for full viewer implementation: no. Direct implementation of full `structure.viewer_3d` is not approved.

## 7. Non-Goals

- no WebGL implementation
- no Three.js integration
- no phonon
- no Brillouin zone implementation
- no external rendering service
- no notebook or script execution
- no artifact JavaScript execution

## 8. Conclusion

PASS. Advanced viewer readiness planning is complete, with `viewer_scene` artifact-contract work recommended next and renderer/full-viewer implementation explicitly not approved.
