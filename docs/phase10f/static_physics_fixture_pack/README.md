# Static Physics Direct-Uploadable Fixture Pack

## Status

candidate_fixture_pack

## Official PASS Claims

None.

This pack is not official PASS evidence. It is a small direct-uploadable fixture pack intended for future replay verification in Phase 10F-5.

## Target Tools

- `structure.coordination_hist`
- `structure.xrd`
- `structure.rdf`

## Scope

This pack provides small text inputs, input manifests, provenance records, and candidate expected contracts. Future replay must run these cases through the existing platform job flow before any fixture-pack result can be recorded.

## Non-Goals

- no official PASS claim
- no notebook execution
- no external script
- no benchmark extraction script
- no external API
- no new adapter
- no full viewer / WebGL / phonon

## Cases

| Case ID | Target Tool | Input | Provenance | Official PASS Eligible | Expected Contract Status |
|---|---|---|---|---:|---|
| `coordination_hist_small_crystal` | `structure.coordination_hist` | `input.cif` | `internal_regression` | false | `candidate_expected_contract` with pending replay numeric values |
| `xrd_small_crystal` | `structure.xrd` | `input.poscar` | `internal_regression` | false | `candidate_expected_contract` with pending replay numeric values |
| `rdf_small_crystal` | `structure.rdf` | `input.poscar` | `internal_regression` | false | `candidate_expected_contract` with pending replay numeric values |

## Provenance

All Phase 10F-4 cases use `internal_regression` provenance. They are copied from existing project-local small structure fixtures so they can support deterministic replay hardening. They are not official examples and cannot become official PASS evidence by themselves.

Only `official_direct` and reviewer-approved `official_derived_manual` cases can become official PASS after direct platform replay and artifact comparison.

## Expected Contracts

Expected contracts separate:

- exact checks for tool id, artifact filenames, schema/security fields, and fixed params;
- numeric checks with explicit tolerances or `pending_replay_generation`;
- metadata checks for required fields, limits, warnings, and provenance;
- security checks for no JavaScript, no external URLs, and no WebGL / Three.js renderer scope.

## Replay

Phase 10F-5 should replay these cases through the platform:

1. Load `manifest.json`.
2. Upload each input through the existing platform resource flow.
3. Submit a deterministic planner/job request for the target tool.
4. Verify selected `tool_id`.
5. Download artifacts.
6. Validate schema/security/exact checks.
7. Generate or compare numeric expected values according to the expected contract.
8. Record fixture-pack results without claiming official PASS.

