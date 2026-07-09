# Phase 10F-3 Static Physics Direct-Uploadable Fixture Pack Planning

## 1. Scope

- planned: a small direct-uploadable fixture-pack design for `structure.coordination_hist`, `structure.xrd`, and `structure.rdf`.
- not created: real fixture inputs, real expected outputs, official PASS evidence, or browser/API replay evidence.
- not executed: notebooks, external scripts, benchmark extraction scripts, external APIs, artifact JavaScript, external URL loading, or real LLM calls.
- not implemented: new adapters, adapter semantic changes, full viewer, WebGL renderer, Three.js, Brillouin-zone 3D, phonon, or advanced local environment classification.

## 2. Baseline

- Phase 10F-1 status: `PARTIAL_PASS`
- Phase 10F-2 status: `PASS`
- Phase 10F-2 commit: `3fd26f9 Plan official static physics coverage gaps`
- current HEAD before Phase 10F-3: `3fd26f93303302c94efc51ff883991085e48beda`
- branch: `master`
- git status before: clean
- official static physics PASS claims before this phase: none

## 3. Fixture Pack Goal

The fixture pack should make a later Phase 10F-4 construction phase possible by defining the smallest safe set of direct-uploadable static-physics cases:

- one coordination-histogram case,
- one XRD case,
- one RDF case,
- explicit provenance labels,
- expected-contract templates,
- numeric tolerance policy,
- replay protocol through the existing platform job flow.

The pack is for future replay verification only. Phase 10F-3 does not create official PASS evidence.

## 4. Non-Goals

- no official PASS claim
- no notebook execution
- no external script execution
- no benchmark extraction script execution
- no external API
- no network workflow
- no new dependency
- no new adapter
- no runtime semantic change
- no full viewer / WebGL / Three.js / phonon

## 5. Proposed Pack Layout

Recommended future layout:

```text
docs/phase10f/static_physics_fixture_pack_plan/
  README.md
  manifest.schema.json
  expected_contract.schema.json
  provenance_policy.md
  tolerance_policy.md
  cases/
    coordination_hist_small_crystal/
      input_manifest.template.json
      expected_contract.template.json
      provenance.template.json
    xrd_small_crystal/
      input_manifest.template.json
      expected_contract.template.json
      provenance.template.json
    rdf_small_crystal/
      input_manifest.template.json
      expected_contract.template.json
      provenance.template.json
```

Phase 10F-3 records this layout only. A later construction phase may create template files or small text fixtures after approval.

## 6. Fixture Selection Policy

Fixture candidates must satisfy all of the following:

1. Direct-uploadable through the existing platform resource flow.
2. Small and text-reviewable.
3. CIF, POSCAR/CONTCAR, or supported Structure JSON.
4. Periodic crystalline structure when required by the target tool.
5. Bounded atom count:
   - coordination histogram: recommended maximum 64 sites.
   - XRD: recommended maximum 128 sites.
   - RDF: recommended maximum 128 sites.
6. No disorder, partial occupancy ambiguity, huge supercells, trajectory data, or notebook-generated hidden state in the first pack.
7. Clear provenance label from the Phase 10F-3 provenance policy.
8. Deterministic expected output under the current tool params.
9. No large benchmark files.
10. No PASS label until replay verification succeeds.

## 7. Tool Coverage

### structure.coordination_hist

- candidate input forms: small CIF, POSCAR, or supported Structure JSON.
- required output artifacts: `coordination_hist.json`, `coordination_hist_plot.json`, `summary.md`, `recipe.json`.
- exact checks: tool id, schema presence, site count, integer histogram counts, dominant coordination bin, limits, security flags.
- tolerance checks: none for histogram counts; optional distances only at adapter rounding precision.

### structure.xrd

- candidate input forms: small crystalline CIF or POSCAR.
- required output artifacts: `xrd_pattern.json`, `xrd_plot.json`, `summary.md`, `recipe.json`.
- exact checks: tool id, schema version, CuKa radiation, artifact names, chart type, security flags.
- tolerance checks: selected two-theta positions and selected relative intensities using the Phase 10F-3 numeric tolerance policy.

### structure.rdf

- candidate input forms: small periodic CIF, POSCAR, or supported Structure JSON.
- required output artifacts: `rdf.json`, `rdf_plot.json`, `summary.md`, `recipe.json`.
- exact checks: tool id, schema version, normalization method, bin count, counts, artifact names, security flags.
- tolerance checks: r grid and selected `g(r)` values using fixed RDF tolerances.

## 8. Expected Contract Policy

Expected contracts must separate:

- exact fields: artifact names, `tool_id`, schema version, chart type, security flags, required top-level keys, deterministic limits.
- tolerance fields: XRD selected peak positions/intensities, RDF selected floating-point values, optional rounded distances.
- security fields: no JavaScript, no script tags, no inline handlers, no external URLs, no CDN, no WebGL, no Three.js.
- metadata fields: local job ids, artifact ids, storage keys, timestamps, hashes.
- provenance fields: label, source, extraction method, reviewer approval status, official PASS eligibility.
- allowed variance: local ids, storage keys, generated timestamps, and content hashes when regenerated from equivalent artifacts.

Tolerance must not hide semantic changes. Any tolerance expansion requires explicit reviewer approval.

## 9. Replay Policy

Future replay should:

1. Load fixture manifest.
2. Upload input through the existing platform resource flow.
3. Submit deterministic planner/job request.
4. Verify selected `tool_id`.
5. Wait for job completion.
6. Download artifacts.
7. Validate schema and security fields.
8. Apply exact and numeric checks.
9. Record result and non-PASS cases.
10. Produce evidence docs.

Replay must not use a real LLM, notebook execution, external scripts, external APIs, artifact JavaScript, external URL loading, or browser/WebGL rendering unless a later evidence phase explicitly approves browser preview.

## 10. Integrity Policy

- `official_direct` and approved `official_derived_manual` are the only labels that can become official PASS after direct replay verification.
- `official_like_curated` and `internal_regression` are useful for regression but are never official PASS by themselves.
- `mapping_only`, `future_scope`, `unsupported`, and `unknown` are non-PASS labels.
- Mapping-only README/gallery cases, notebook-only cases, script-heavy cases, external-API cases, and future-scope cases must remain non-PASS.
- This phase adds no official PASS claim.

## 11. Recommended Phase 10F-4

Recommended next phase:

```text
Phase 10F-4: Static Physics Direct-Uploadable Fixture Pack Construction
```

Scope for Phase 10F-4 should be limited to constructing a small approved fixture pack and expected-contract files from these templates. It should not run official PASS verification unless explicitly approved, and it must not implement a new adapter, execute notebooks/scripts, use external APIs, or enter full viewer / WebGL / phonon.

## 12. Conclusion

PASS. Phase 10F-3 defines the fixture-pack layout, selection policy, provenance labels, expected-contract templates, numeric tolerances, replay protocol, and Phase 10F-4 scope without creating official PASS evidence or executing prohibited workflows.
