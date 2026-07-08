# XRD Artifact Contract Audit

## xrd_pattern.json
- schema_version: `phase10e4.xrd_pattern.v1`
- tool_id: `structure.xrd`
- source, structure summary, parameters, pattern peaks, limits, warnings, and security sections are present.
- peaks are sorted by `two_theta_deg` and numeric values are rounded deterministically.
- radiation is `CuKa`; intensity scale is relative to 100.

## xrd_plot.json
- schema_version: `phase10e4.static_chart.v1`
- tool_id: `structure.xrd`
- chart_type: `stem`
- x/y axes, series, metadata, and security sections are present.

## summary.md
Contains Input, Method, Results, Limits, and Security sections. It does not claim experimental refinement, Rietveld refinement, profile fitting, peak broadening, or official example reproduction.

## recipe.json
- schema_version: `phase10e4.recipe.v1`
- deterministic: true
- dependencies.new_dependencies_added: false
