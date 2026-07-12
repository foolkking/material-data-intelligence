# Viewer Performance Budget

| Resource | Interactive | Degraded maximum | Refusal |
| --- | ---: | ---: | --- |
| Displayed atoms | 1,000 | 2,048 | above 2,048 |
| Displayed bonds | 4,096 | 8,192 | above 8,192 |
| Style groups / atom draws | 32 | 32 | above 32 |
| Total draw calls | 40 | 40 | metric failure |
| Geometries | 5 | 5 | metric failure |
| Materials | 39 | 39 | metric failure |

Interactive uses DPR cap 2 and antialiasing. Degraded uses DPR cap 1 and no
antialiasing. Thresholds are code constants and cannot be artifact-controlled.
