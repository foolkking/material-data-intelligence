# Phase 10F-10: Viewer Scene Contract Evidence Closure

## Goal

Close the Phase 10F-9 viewer scene contract fixture evidence and decide whether JSON-only browser preview evidence should be captured before any renderer work.

## Scope

- Read Phase 10F-9 fixture pack, validator, tests, and evidence docs.
- Confirm fixture replay results.
- Optionally replay JSON-only artifact preview through existing static preview surface if available.
- Record browser/API evidence only for inert JSON preview.
- Keep renderer evidence deferred.

## Not In Scope

- Do not implement full `structure.viewer_3d`.
- Do not implement WebGL.
- Do not introduce Three.js.
- Do not add a renderer bundle.
- Do not add planner routing.
- Do not add a new adapter.
- Do not execute notebooks or external scripts.
- Do not implement phonon, Brillouin-zone 3D, or advanced local environment classification.

## PASS Criteria

- Phase 10F-9 validator tests remain passing.
- Fixture and manifest evidence is complete.
- JSON-only preview evidence is either captured or explicitly deferred with reason.
- No artifact JavaScript or external URLs are introduced.
- Renderer and full viewer implementation remain `NOT_READY`.
