# Phase 10F-15 Instancing and Performance

Evidence environment: Chrome 149, Firefox 128, WebKit 18 on Windows; software WebGL 2 where reported.

| Case | Atoms | Bonds | Instanced meshes | Draw calls | Init ms | First frame ms |
|---|---:|---:|---:|---:|---:|---:|
| minimal Si | 2 | 1 | 1 | 3 | see evidence | see evidence |
| NaCl | 2 | 0 | 2 | 4 | see evidence | see evidence |
| near cap | 256 | 2048 | 2 | 4 | see evidence | see evidence |

The canonical evidence snapshot records the exact values for the final run. Near-cap rendering completes inside the bounded runner timeout, interactions remain executable, and tab disposal/remount produces zero then one canvas. No FPS or unsupported hardware claim is made.
