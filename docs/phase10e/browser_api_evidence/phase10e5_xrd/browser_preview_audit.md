# XRD Browser Preview Audit

The browser evidence uses local static preview pages for the generated XRD job and artifacts.

- `01_job_completed.html`: completed job summary.
- `02_artifact_list.html`: all four expected artifacts.
- `03_xrd_pattern_json_preview.html`: schema-aware JSON preview with peak table.
- `04_xrd_plot_preview.html`: static chart JSON preview; rendered stem chart UI is deferred.
- `05_summary_preview.html`: summary markdown text preview.
- `06_recipe_preview.html`: deterministic recipe JSON preview.

No full 3D viewer, WebGL canvas, renderer bundle, or external resource loading is used.
