# Phase 10H Resource Caps

| Resource | Cap |
|---|---:|
| Atoms | 512 |
| Branches | 1536 |
| Q-points | 4096 |
| Path segments | 256 |
| Labels | 512 |
| Label characters | 64 |
| DOS grid points | 100000 |
| Projected DOS series | 512 |
| Total numeric values | 4000000 |
| Degeneracy groups | 4096 |
| Source metadata bytes | 16384 |
| Warnings | 32 |
| Artifact bytes | 64000000 |

Validation checks `qpoints * branches` and `dos_points * (projected_series + 2)` using division-based overflow-safe preflight. Arrays are not expanded, resampled, or allocated based on untrusted products before this check. Nesting depth, visited nodes, and numeric magnitude are also bounded.
