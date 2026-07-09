# Artifact Comparison Report

## Result

No official static physics artifact comparison was performed because no official examples benchmark case passed the Phase 10F-1 direct-uploadable gate for `structure.coordination_hist`, `structure.xrd`, or `structure.rdf`.

## Expected Comparison Policy

If a future direct-uploadable official static physics case is added, compare:

- `structure.coordination_hist`
  - `coordination_hist.json`
  - `coordination_hist_plot.json`
  - `summary.md`
  - `recipe.json`
  - exact integer counts where expected official numeric data exists
- `structure.xrd`
  - `xrd_pattern.json`
  - `xrd_plot.json`
  - `summary.md`
  - `recipe.json`
  - tolerance-pinned peak positions/intensities only when expected numeric data exists
- `structure.rdf`
  - `rdf.json`
  - `rdf_plot.json`
  - `summary.md`
  - `recipe.json`
  - deterministic r-grid, bin count, selected counts, and g(r) values only when expected numeric data exists

## Security Fields Required For Any Future PASS

- `security.contains_javascript == false`
- `security.external_urls == []`
- `security.external_urls_allowed == false`
- no HTML renderer bundle
- no WebGL or Three.js artifact

## Current Phase 10F-1 Official PASS Claims

None.
