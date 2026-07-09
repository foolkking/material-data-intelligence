# Phase 10F-3 Numeric Tolerance Policy

## 1. Scope

This policy defines numeric comparison tolerances for future static physics direct-uploadable fixture replay. It does not execute verification and does not create PASS evidence.

## 2. Exact Fields

Always exact:

- `tool_id`
- schema version
- artifact filenames
- static chart `chart_type`
- security fields:
  - `contains_javascript == false`
  - `external_urls == []`
  - `external_urls_allowed == false`
- coordination histogram integer counts
- RDF integer counts
- resource-cap fields when deterministic for the case

## 3. coordination_hist

Recommended checks:

- `structure.site_count`: exact
- histogram bin labels/order: exact
- histogram counts: exact
- dominant coordination number/count: exact
- pair counts: exact when included

No floating-point tolerance should be needed for primary histogram assertions.

## 4. XRD

Recommended checks:

- `radiation`: exact, `CuKa`
- selected `two_theta_deg`: tolerance `+-0.02`
- selected relative intensity: tolerance `+-0.5`
- selected d-spacing, if checked: tolerance `+-0.000001` after adapter rounding
- peak count: exact when same params and dependency versions are fixed; otherwise bounded range with explicit rationale
- strongest peak: exact by selected rounded two-theta when stable

XRD tolerance must not be widened to hide changed radiation policy, range filtering, thresholding, or peak ordering.

## 5. RDF

Recommended checks:

- `normalization`: exact, `number_density`
- bin count: exact
- `r_angstrom` grid: tolerance `+-0.000001`
- `bin_edges_angstrom`: tolerance `+-0.000001`
- counts: exact
- selected `g_r` values: tolerance `+-0.000001` for deterministic internal fixtures
- number density: tolerance `+-0.000001` after adapter rounding
- partial pair ordering: exact by `center_element`, `neighbor_element`

RDF tolerance must not be widened to hide changed cutoff, bin width, periodic-image policy, normalization, or partial-pair policy.

## 6. Metadata Exact vs Flexible Fields

Exact:

- artifact names
- schema versions
- `tool_id`
- chart type
- security flags
- params that affect numeric output

Flexible / metadata-only:

- job id
- plan id
- artifact id
- local storage key
- timestamps
- generated content hash when artifacts are regenerated under an approved replay

## 7. Warnings

- Required warnings may be asserted by warning code.
- Allowed warnings may vary only when documented by the adapter contract.
- Warning order should be stable if the adapter promises stable ordering; otherwise compare by set of warning codes.

## 8. Determinism Requirements

Future fixture replay must require:

- stable params serialization,
- stable artifact filenames,
- stable series ordering,
- stable bin/peak ordering,
- adapter-defined rounding,
- no dependency installation during replay,
- no real LLM planning.

## 9. Approval Rule

Tolerance must not be used to hide semantic changes. Any tolerance change requires explicit reviewer approval and an update to the expected contract rationale.
