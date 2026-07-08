# Artifact Contract Audit

## Verdict
PASS

## coordination_hist.json
- schema_version: phase10e1.coordination_hist.v1
- tool_id: structure.coordination_hist
- histogram bins sorted by coordination_number
- site_details sorted by site_index when present
- pair_counts sorted deterministically when present
- security flags show no artifact JavaScript and no external URLs

## coordination_hist_plot.json
- schema_version: phase10e1.static_chart.v1
- chart_type: bar
- static JSON chart artifact only
- security flags show no artifact JavaScript and no external URLs

## summary.md
- Includes Input, Method, Results, Limits, and Security sections.
- Does not claim VoronoiNN, CrystalNN, or advanced local environment classification.

## recipe.json
- schema_version: phase10e1.recipe.v1
- deterministic: true
- dependencies.new_dependencies_added: false
