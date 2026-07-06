# Phase 10A-2 Browser/API Evidence Index

- generatedAt: 2026-07-06T05:15:33.768374+00:00
- planner mode: Mock Planner
- used real LLM: no
- evidence level: Browser + API + Artifact

## Statistics

| Metric | Count |
|---|---:|
| total_cases | 6 |
| pass | 6 |
| partial | 0 |
| fail | 0 |

## Cases

| Case | Adapter | Verdict | Dataset | Job | Plan | Artifacts |
|---|---|---|---|---|---|---|
| matpes_histogram | viz.histogram | PASS | dataset_0008 | job_d287f0004848447681c53e42 | plan_5715df36c22b4a2c8ad298b4 | histogram.json, histogram.html, summary.md, recipe.json |
| matpes_scatter | viz.scatter | PASS | dataset_0007 | job_67db9db18f044a638f580f41 | plan_be9e1d0fdd524972bf6b68c8 | scatter.json, scatter.html, summary.md, recipe.json |
| ward_composition_summary | composition.summary | PASS | dataset_0001 | job_b7d2f69b76e7431f96e3d85e | plan_f6c98d2d2835438689364ddf | composition_summary.json, summary.md, recipe.json |
| ward_correlation | viz.correlation | PASS | dataset_0011 | job_f3faed1162134846b4c8c48f | plan_b97cba0c2fd249cfac00cfca | correlation_matrix.json, correlation_heatmap.json, correlation_heatmap.html, summary.md, recipe.json |
| ward_distribution | table.distribution_summary | PASS | dataset_0009 | job_bcaab519b99f43159f09cef0 | plan_ad845d07ccf04029943512e7 | distribution_summary.json, summary.md, recipe.json |
| ward_histogram | viz.histogram | PASS | dataset_0010 | job_e4b44a680fb24fb6bab9c69b | plan_334f21237d9b4dcc842c54b2 | histogram.json, histogram.html, summary.md, recipe.json |

## Boundaries

- This evidence pack uses local Mock Planner and does not call a real LLM.
- It does not overwrite the desktop benchmark pack.
- It validates only the two DIRECT_VERIFIED official cases and the six Phase 10A-1 adapter scenarios.
- Remaining official pymatviz examples are not implied to be verified by this evidence pack.
