# Phase 10F-15 Cap Alignment

| Layer | Sites | Bonds | Species | JSON bytes | Behavior |
|---|---:|---:|---:|---:|---|
| canonical validator | 256 | 2048 | 32 | 1,000,000 | reject invalid/over-cap |
| adapter hard cap | 256 | 2048 | 32 | 1,000,000 | strict params; bounded bond generation with warnings |
| renderer hard cap | 256 | 2048 | 32 | 1,000,000 | validation fallback, no canvas |
| production recommended | 256 | 2048 | 32 | 1,000,000 | fully render with instancing |

Truncation belongs to the adapter contract policy, never the renderer. A canonical scene is rendered in full or refused with JSON fallback. At-cap evidence uses 256 atoms and 2048 bonds; above-cap mapper tests reject initialization.
