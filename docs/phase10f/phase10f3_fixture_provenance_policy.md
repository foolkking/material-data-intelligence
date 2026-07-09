# Phase 10F-3 Fixture Provenance Policy

## 1. Purpose

This policy defines provenance labels for future static physics direct-uploadable fixtures. It prevents curated or internal fixtures from being mislabeled as official PASS evidence.

## 2. Labels

### `official_direct`

Input artifact is directly present in the official benchmark pack and can be uploaded without transformation.

Requirements:

- local official input file is present;
- no notebook execution;
- no script execution;
- no external API;
- no network;
- expected contract can be derived from an existing official expected output or a directly verified official artifact;
- platform replay must succeed before PASS.

Eligibility: can become official PASS only after direct platform replay and artifact comparison pass.

### `official_derived_manual`

Input is manually extracted from official documentation or examples without executing notebooks, scripts, external APIs, or network workflows.

Requirements:

- source path and extraction rationale are recorded;
- manual extraction is small and reviewable;
- reviewer approval is recorded before official PASS eligibility;
- expected contract is reviewed separately;
- platform replay must succeed before PASS.

Eligibility: can become official PASS only after reviewer approval, direct platform replay, and artifact comparison pass.

### `official_like_curated`

Curated small fixture inspired by official examples or official semantics, but not directly official.

Requirements:

- source inspiration may be recorded;
- no claim that the input is official;
- expected contract can be used for regression.

Eligibility: never official PASS by itself.

### `internal_regression`

Existing internal Phase 10E fixture or platform-generated case.

Requirements:

- source is recorded as project-internal;
- may reuse existing small CIF, POSCAR, or Structure JSON fixtures;
- useful for deterministic replay and regression.

Eligibility: never official PASS by itself.

### `mapping_only`

Case maps conceptually to a future or adjacent capability but lacks direct-uploadable input and expected contract.

Eligibility: never PASS.

### `future_scope`

Case belongs to a deferred capability such as full viewer, WebGL, Brillouin-zone 3D, phonon, widget execution, or advanced local environment classification.

Eligibility: never PASS in the static physics fixture pack.

### `unsupported`

Case is outside the target tool family or violates the direct-uploadable gate.

Eligibility: never PASS.

### `unknown`

Provenance cannot be determined from available local metadata.

Eligibility: never PASS until reclassified.

## 3. Official PASS Rule

Only `official_direct` and approved `official_derived_manual` can become official PASS after direct replay verification.

`official_like_curated`, `internal_regression`, `mapping_only`, `future_scope`, `unsupported`, and `unknown` must not be written as official PASS.

## 4. Required Provenance Fields

Future `provenance.json` files should include:

```json
{
  "label": "official_like_curated",
  "source_pack_case_id": null,
  "source_path": null,
  "manual_extraction": false,
  "notebook_executed": false,
  "script_executed": false,
  "external_api_used": false,
  "network_used": false,
  "reviewer_approval_required": true,
  "reviewer_approved": false,
  "official_pass_eligible": false,
  "notes": []
}
```

The default must be non-PASS until explicitly proven otherwise.
