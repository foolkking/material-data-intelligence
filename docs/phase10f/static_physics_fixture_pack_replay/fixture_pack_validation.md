# Fixture Pack Validation

## Command Class

Validation used a local Python harness that parsed the fixture pack, JSON schemas, case manifests, expected contracts, and provenance files. It did not execute notebooks, external scripts, benchmark extraction scripts, network calls, or real LLM calls.

## Results

- `manifest.json`: PASS
- `manifest.schema.json`: PASS
- `expected_contract.schema.json`: PASS
- case directories present: PASS
- `input_manifest.json` files parse: PASS
- `expected_contract.json` files parse: PASS
- `provenance.json` files parse: PASS
- input files present: PASS
- input size limit `<= 20 KB`: PASS
- `official_pass_claims == false`: PASS
- `official_pass_claim == false`: PASS for all cases
- provenance labels valid: PASS
- target tools limited to static physics family: PASS
- notebooks/scripts/archives absent: PASS
- runtime JSON/CIF/POSCAR external URL dependency absent: PASS

Markdown files contain documentation-only references to deferred WebGL/Three.js scope. These are false positives for the text scan and are not replay dependencies.

## Cases

- `coordination_hist_small_crystal`: `internal_regression`, direct-uploadable CIF
- `xrd_small_crystal`: `internal_regression`, direct-uploadable POSCAR
- `rdf_small_crystal`: `internal_regression`, direct-uploadable POSCAR
