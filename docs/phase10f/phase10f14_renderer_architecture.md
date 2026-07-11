# Phase 10F-14 Renderer Architecture

## Components

- `viewerSceneRendererValidation.ts`: frontend canonical gate and resource/security caps.
- `viewerSceneRendererMapper.ts`: whitelist mapping into immutable renderer-owned values.
- `viewerSceneRendererGeometry.ts`: lattice edges, bonds, bounds and camera math.
- `viewerSceneRendererEngine.ts`: Three.js scene, renderer, OrbitControls and disposal.
- `ViewerSceneRendererSurface.tsx`: React state, fallback, controls and evidence selectors.

The engine never receives the raw artifact. Artifact strings cannot choose modules, DOM identifiers, CSS selectors, shaders, textures, callbacks or URLs.

Rendering is demand-based. OrbitControls `change`, resize, reset and visibility toggles request frames; there is no continuous animation loop.
