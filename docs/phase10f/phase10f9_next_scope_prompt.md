# Phase 10F-9：Viewer Scene JSON Preview Evidence / Contract Fixture Planning

## Goal

Enter Phase 10F-9 to plan and, if approved by the phase prompt, prepare JSON-only viewer scene contract fixtures and evidence for inert `viewer_scene` artifacts.

This phase must not implement full `structure.viewer_3d`, WebGL, Three.js, a renderer bundle, frontend 3D components, phonon, Brillouin-zone 3D, or advanced local environment classification.

## Baseline

Use Phase 10F-8 as the baseline:

- viewer_scene artifact contract planning: `READY`
- JSON-only preview planning: `READY`
- renderer handoff: `PARTIAL_READY`
- renderer implementation: `NOT_READY`
- full `structure.viewer_3d` implementation: `NOT_READY`

## Scope

Allowed:

- read Phase 10F-8 contract documents;
- define small inert `viewer_scene.json` contract fixtures;
- define manifest fixture expectations;
- plan or capture JSON-only static preview evidence;
- validate security flags and caps/warnings visibility;
- update docs and persistent state.

Forbidden:

- no full `structure.viewer_3d` implementation;
- no WebGL renderer;
- no Three.js;
- no renderer bundle;
- no new frontend 3D runtime;
- no planner routing changes;
- no new adapter;
- no Tool Registry runtime behavior changes;
- no notebook execution;
- no external scripts;
- no external API calls;
- no artifact JavaScript;
- no external URLs in artifact data;
- no phonon, Brillouin-zone 3D, or advanced local environment classifier implementation.

## Required Inputs

Read:

- `docs/phase10f/phase10f8_viewer_scene_artifact_contract_planning.md`
- `docs/phase10f/phase10f8_viewer_scene_json_contract.md`
- `docs/phase10f/phase10f8_viewer_scene_manifest_contract.md`
- `docs/phase10f/phase10f8_viewer_scene_validation_contract.md`
- `docs/phase10f/phase10f8_viewer_scene_security_contract.md`
- `docs/phase10f/phase10f8_viewer_scene_browser_evidence_contract.md`
- `docs/phase10f/phase10f8_viewer_scene_versioning_strategy.md`
- `docs/phase10f/phase10f8_viewer_scene_contract_readiness_matrix.md`
- Phase 10D static preview evidence and existing `viewer_scene.json` / `viewer_assets_manifest.json` examples.

## Evidence Rules

- JSON-only preview evidence may show schema-aware static preview or raw JSON preview.
- Renderer screenshot evidence remains deferred.
- Browser evidence must state that no renderer bundle, WebGL, Three.js, artifact JavaScript, or external URL request was invoked.
- If screenshots are captured, they must be real browser-rendered frontend pages.

## PASS Criteria

- Contract fixture plan or JSON-only evidence plan is complete.
- Security/no-external-URL boundary is preserved.
- No renderer implementation is added.
- No full `structure.viewer_3d` implementation is added.
- No planner routing or Tool Registry runtime behavior is changed.
- Docs and persistent state are updated.
- Checks pass or any skipped checks are explicitly justified.

## FAIL Criteria

- Implements full viewer, WebGL, Three.js, renderer bundle, or phonon.
- Adds artifact JavaScript or external URL dependencies.
- Changes planner routing or registry/runtime behavior without approval.
- Executes notebooks, external scripts, external APIs, or real LLM paths.
- Claims renderer evidence from JSON-only preview.

## Recommended Next

If Phase 10F-9 succeeds, decide whether to proceed to a no-renderer `viewer_scene` schema/fixture implementation phase or continue readiness gap closure. Do not directly enter full `structure.viewer_3d` implementation / WebGL implementation / Three.js integration / phonon implementation.
