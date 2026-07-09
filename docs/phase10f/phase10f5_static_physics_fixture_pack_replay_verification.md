# Phase 10F-5 Static Physics Fixture Pack Replay Verification

## 1. Scope

- replayed: Phase 10F-4 static physics fixture pack
- tools: `structure.coordination_hist`, `structure.xrd`, `structure.rdf`
- not claimed: official examples PASS
- not implemented: new adapters, full viewer, WebGL renderer, Three.js renderer, phonon, notebook/script extraction

## 2. Baseline

- Phase 10F-4 commit: `28827c1 Construct static physics fixture pack`
- Phase 10F-4 HEAD: `28827c125c5f602c565db3412b9c25cc5e6369ff`
- current HEAD before: `28827c125c5f602c565db3412b9c25cc5e6369ff`
- branch: `master`
- git status before: clean

## 3. Fixture Pack Validation

- manifest: PASS
- schemas: PASS
- cases: 3 present
- provenance: all `internal_regression`
- `official_pass_claims`: false
- per-case `official_pass_claim`: false
- input files: present and below 20 KB
- notebooks/scripts/archives: absent
- external URL dependency: absent

## 4. Replay Results

### coordination_hist_small_crystal

- selected tool: `structure.coordination_hist`
- worker status: completed
- artifacts: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, `recipe.json`
- fixture-pack result: PASS

### xrd_small_crystal

- selected tool: `structure.xrd`
- worker status: completed
- artifacts: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, `recipe.json`
- fixture-pack result: PASS

### rdf_small_crystal

- selected tool: `structure.rdf`
- worker status: completed
- artifacts: `rdf.json`, `rdf_plot.json`, `summary.md`, `recipe.json`
- fixture-pack result: PASS

## 5. Expected Contract Updates

- candidate replay values: generated for all 3 cases
- pending fields: none for selected numeric checks
- official PASS claims: none
- added `candidate_replay` metadata with `official_pass_claim: false`

## 6. Artifact Validation

- coordination histogram: schema, tool id, static chart, summary, recipe, security, site count, and histogram checks passed
- XRD: schema, tool id, static chart, summary, recipe, security, radiation, peak count, selected peaks, and strongest peak checks passed
- RDF: schema, tool id, static chart, summary, recipe, security, normalization, PBC, bin count, selected grid/value samples, and counts checks passed

## 7. Security

- no JS: PASS
- no external URLs: PASS
- no WebGL renderer: PASS
- no notebook/script execution: PASS
- no real LLM: PASS
- no secrets: `NO_SECRET_PATTERN_HITS`

## 8. Result Boundary

Phase 10F-5 may claim fixture-pack replay PASS. It does not claim official examples PASS because the three replayed cases use `internal_regression` provenance and are not eligible official cases.

## 9. Deferred Scope

- official PASS evidence
- official-derived fixture approval
- full viewer
- WebGL
- Three.js
- phonon
- advanced local environment classification

## 10. Conclusion

PASS
