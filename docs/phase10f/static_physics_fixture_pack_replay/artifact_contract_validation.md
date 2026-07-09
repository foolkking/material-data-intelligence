# Artifact Contract Validation

## Common Checks

- selected `tool_id` matches expected tool: PASS
- expected artifact filenames generated: PASS
- artifact files non-empty: PASS
- primary JSON `tool_id` exact: PASS
- plot JSON `tool_id` exact: PASS
- `security.contains_javascript == false`: PASS
- `security.external_urls == []`: PASS
- `security.external_urls_allowed == false`: PASS
- `recipe.json` `deterministic == true`: PASS
- `recipe.json` `dependencies.new_dependencies_added == false`: PASS

## coordination_hist_small_crystal

- `coordination_hist.json`: `phase10e1.coordination_hist.v1`
- `coordination_hist_plot.json`: `phase10e1.static_chart.v1`
- `recipe.json`: `phase10e1.recipe.v1`
- `site_count`: 1
- `coordination_numbers`: `[0]`
- `histogram_counts`: `[1]`
- `dominant_coordination`: 0

## xrd_small_crystal

- `xrd_pattern.json`: `phase10e4.xrd_pattern.v1`
- `xrd_plot.json`: `phase10e4.static_chart.v1`
- `recipe.json`: `phase10e4.recipe.v1`
- `radiation`: `CuKa`
- `peak_count`: 23
- selected `two_theta_deg`: `[15.711913, 22.290756, 27.388668]`
- selected relative-100 `intensity`: `[5.75318, 100.0, 1.53833]`
- strongest peak: `two_theta_deg = 22.290756`, `intensity = 100.0`, `hkl = [1, 1, 0]`

## rdf_small_crystal

- `rdf.json`: `phase10e7.rdf.v1`
- `rdf_plot.json`: `phase10e7.static_chart.v1`
- `recipe.json`: `phase10e7.recipe.v1`
- `normalization`: `number_density`
- `pbc`: `[true, true, true]`
- `bin_count`: 8
- sample indices: `[0, 1, 4, 7]`
- sample `r_grid`: `[0.25, 0.75, 2.25, 3.75]`
- sample `g(r)`: `[0.0, 0.0, 0.0, 0.0]`
- full counts: `[0, 0, 0, 0, 0, 0, 0, 0]`
- number density: `0.011147`

## False Positives

`summary.md` artifacts mention "no WebGL renderer" as a security statement. This is a text-scan false positive, not a WebGL dependency or executed renderer.
