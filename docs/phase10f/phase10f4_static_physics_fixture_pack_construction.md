# Phase 10F-4 Static Physics Fixture Pack Construction

## 1. Scope

- constructed: a small direct-uploadable static physics fixture pack for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- not verified: no official PASS verification, no fixture-pack replay verification, no browser/API evidence, no generated numeric expected values.
- not implemented: no new adapter, no adapter semantic change, no full viewer, no WebGL renderer, no Three.js, no Brillouin-zone 3D, no phonon, no advanced local environment classification.

## 2. Baseline

- Phase 10F-3 commit: `8314a1a Plan static physics fixture pack`
- Phase 10F-3 HEAD: `8314a1ac99eff1cc3aa622b5fa27883eada75971`
- current HEAD before Phase 10F-4: `8314a1ac99eff1cc3aa622b5fa27883eada75971`
- branch: `master`
- git status before: clean
- Phase 10F-1 status retained: `PARTIAL_PASS`
- official static physics PASS claims before this phase: none

## 3. Fixture Pack

- path: `docs/phase10f/static_physics_fixture_pack/`
- status: `candidate_fixture_pack`
- target tools:
  - `structure.coordination_hist`
  - `structure.xrd`
  - `structure.rdf`
- case count: 3
- official PASS claims: none

## 4. Cases

### coordination_hist_small_crystal

- input: `cases/coordination_hist_small_crystal/input.cif`
- target tool: `structure.coordination_hist`
- provenance: `internal_regression`
- source: project-local `tests/fixtures/structures/simple_cubic.cif`
- expected artifacts: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, `recipe.json`

### xrd_small_crystal

- input: `cases/xrd_small_crystal/input.poscar`
- target tool: `structure.xrd`
- provenance: `internal_regression`
- source: project-local `tests/fixtures/structures/nacl.poscar`
- expected artifacts: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, `recipe.json`

### rdf_small_crystal

- input: `cases/rdf_small_crystal/input.poscar`
- target tool: `structure.rdf`
- provenance: `internal_regression`
- source: project-local `tests/fixtures/structures/nacl.poscar`
- expected artifacts: `rdf.json`, `rdf_plot.json`, `summary.md`, `recipe.json`

## 5. Provenance

- labels used: `internal_regression`
- official pass eligibility: false for all constructed cases.
- reviewer approval needs: official PASS would require `official_direct` or approved `official_derived_manual` provenance, direct replay verification, and reviewer approval.

## 6. Expected Contracts

- exact checks: tool id, artifact filenames, fixed params where applicable, and security flags.
- numeric checks:
  - coordination histogram site count / histogram counts / dominant coordination are `pending_replay_generation`.
  - XRD peak count / selected two-theta / relative intensity / strongest peak are `pending_replay_generation`.
  - RDF bin count / r grid / selected `g(r)` / counts are `pending_replay_generation`.
- security checks: no JavaScript, no external URLs, external URLs not allowed.
- pending fields: all numeric expected values that require platform replay output.

## 7. Validation

- schema: manifest and expected-contract schemas were added without external schema URLs.
- size: inputs are small text files below the 20 KB per-input limit.
- security: fixture pack contains no artifact JavaScript, no external URL dependency, and no renderer bundle.
- no notebook/script: no notebook, executable script, binary archive, screenshot, or generated browser evidence was added.

## 8. Security / Integrity

- no JS: fixture pack uses static JSON, Markdown, CIF, and POSCAR text files only.
- no external URLs: replay has no external URL dependency.
- no notebook execution: none performed.
- no external script: none performed.
- no real LLM: none used.
- no fabricated official PASS: all `official_pass_claim` fields are false.

## 9. Deferred Scope

- replay verification: Phase 10F-5.
- official PASS evidence: deferred until eligible official provenance and direct replay exist.
- full viewer: deferred.
- WebGL: deferred.
- phonon: deferred.

## 10. Conclusion

PASS. Phase 10F-4 constructs a bounded candidate fixture pack with manifest, schemas, case inputs, input manifests, expected contracts, provenance files, and README files, while keeping official PASS claims at none.

