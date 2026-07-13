# Phase 10F-25 Clipping, Cell, and Camera Controls

Phase 10F-25 adds renderer-local spatial controls to the validated periodic
structure viewer. The implementation provides bounded axis-aligned clipping,
independent canonical-cell and supercell-boundary visibility, lattice axes,
and deterministic camera presets. It does not modify the canonical scene,
lattice, sites, periodic identity, bonds, measurements, or backend runtime.

## Architecture

`ViewerViewControls` owns accessible React controls. `viewerSceneViewState`
owns validation and inert serialization. `ViewerRendererEngine` translates the
validated state to application-owned Three.js planes, line geometry, and camera
positions. The engine remains demand-rendered and uses one WebGL context.

Picking applies the same active clipping planes to ray intersections, so a
visually clipped atom cannot remain selectable. Measurement values continue to
use validated world coordinates and do not change when clipping changes.

## Readiness

Clipping foundation, X/Y/Z planes, cell display, outer supercell boundary,
lattice axes, camera presets, state serialization, picking/measurement
integration, accessibility, mobile, performance, and security are READY.
The full scientific viewer remains PARTIAL_READY. Export productization,
trajectory, phonon, Brillouin-zone, and volumetric work remain NOT_READY.
