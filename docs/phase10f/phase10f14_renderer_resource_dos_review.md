# Phase 10F-14 Renderer Resource DoS Review

The renderer rechecks 256 sites, 2048 bonds, 32 species, `[1,1,1]` expansion and 1 MB JSON. Pixel ratio is capped at 2, sphere segments are application-owned, materials and geometry are shared, rendering is demand-based and no labels or recursive artifact nodes are accepted.

A near-cap mapper smoke test covers 256 sites and 2048 bonds. Browser evidence covers repeated mount/unmount and context loss. Production optimization with instancing is deferred but no unbounded growth path is present in the foundation.
