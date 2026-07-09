# Phase 10F-2 Expected Contract Authoring Plan

## 1. Purpose

This plan defines how future `expected_contract.json` files should be authored for static structure physics direct verification. It is planning only and does not create official PASS evidence.

## 2. Contract Layout

Each static physics expected contract should contain:

- `case_id`
- `candidate_tool`
- `fixture_provenance`
- `input_manifest`
- `expected_artifacts`
- `schema_assertions`
- `field_assertions`
- `numeric_tolerances`
- `security_assertions`
- `allowed_variance`
- `pass_claim_policy`

## 3. Exact Fields

Exact fields should include:

- artifact names
- `tool_id`
- schema version
- chart type
- required top-level keys
- security flags:
  - `contains_javascript == false`
  - `external_urls == []`
  - `external_urls_allowed == false`
- deterministic limits/cap fields when independent of numeric method output.

## 4. Numeric Fields With Tolerance

Use tolerance only for fields that may vary through floating-point calculation while remaining physically and contractually equivalent.

- coordination histogram:
  - histogram integer counts exact
  - optional distances checked at adapter rounding precision
- XRD:
  - selected `two_theta_deg` values with fixed degree tolerance
  - selected relative intensities with fixed absolute or relative tolerance
  - selected d-spacings with adapter rounding tolerance
- RDF:
  - r grid/bin centers exact after rounding
  - counts exact
  - selected `g_r` and density values with fixed tolerance

## 5. Security-Critical Fields

Security-critical fields must never be tolerant or optional:

- no artifact JavaScript
- no active script tags
- no inline event handlers
- no external URLs
- no CDN references
- no WebGL/Three.js renderer references
- no arbitrary local path reads
- no notebook/script execution metadata
- no real LLM requirement

## 6. Metadata-Only Fields

Metadata-only fields may be checked for presence without exact equality:

- generated timestamps, if any
- local job IDs
- artifact IDs
- content hashes when regenerated in a new run
- local storage keys
- frontend URL references

These fields should not determine official PASS unless a future phase explicitly pins a replay environment.

## 7. Allowed to Vary

Allowed-to-vary fields should be documented per case:

- local path prefixes
- job IDs and plan IDs
- generated artifact IDs
- content hashes across approved re-generation if numeric and schema assertions pass
- warning order only if the adapter contract says warnings are stable by code; otherwise require sorted warnings.

## 8. Avoiding Overfitting

Expected contracts should avoid overfitting by:

- checking selected representative peaks/bins rather than every floating-point value when not required;
- checking exact integer counts and schema/security fields;
- recording tolerances with rationale;
- using at least one positive and one boundary-style check per tool where possible;
- separating official-derived provenance from internal regression fixtures.

## 9. Provenance Labels

Use one of:

- `official_direct`: existing official direct-uploadable source artifact.
- `official_derived_manual`: manually curated from official source material without executing notebook/script/API workflows.
- `official_like_curated`: small fixture designed to match official tool semantics but not official source evidence.
- `internal_regression`: platform fixture only; never an official PASS claim.

## 10. PASS Policy

An official-derived fixture does not become official PASS evidence unless provenance and the direct-uploadable gate are satisfied, the case is executed through the platform, and generated artifacts are compared to the approved expected contract.

Mapping-only, notebook-only, script-heavy, external-API, future-scope, screenshot-only, and missing-input cases must not be written as PASS.

