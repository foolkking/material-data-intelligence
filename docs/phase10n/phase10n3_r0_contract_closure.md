# Phase 10N-3 R0 Experimental XRD Exact Contract Closure

Status: `SEALED_FOR_PHASE_10N3_IMPLEMENTATION`

## Authority

- Tool: `structure.experimental_xrd_comparison@0.1.0`.
- Theoretical authority: persisted `structure.xrd` table Artifact with payload contract
  `phase10e4.xrd_pattern.v1`, produced by `XrdPatternAdapter@0.1.0`.
- Detector: `mdi.experimental_xrd_peak_detection@1.0.0`, using locked
  `scipy.signal.find_peaks` from SciPy `1.17.1`.
- Matcher: `mdi.xrd_ordered_position_match@1.0.0`, deterministic one-to-one assignment
  over tolerance-qualified pairs ordered by absolute 2theta residual and exact identities.
- Artifact: `phase10n3.experimental_xrd_comparison.v1` in inert `table_json`; optional
  `plotly_json`, `summary_md` and `recipe_json` are consumers of the same result.

N3 resolves an exact persisted theoretical Artifact and never calculates a theoretical
pattern. Existing theoretical hkl and multiplicity remain source metadata and are not
recomputed or represented as experimental indexing.

## Experimental Resource 1.0

The strict resource uses `schemaVersion=phase10n3.experimental_xrd_resource.v1`, exact
`resourceId`, `resourceVersion`, `resourceHash`, `xAxis.kind=two_theta`,
`xAxis.unit=degree`, a strictly increasing finite `twoTheta` array, an equal-length finite
non-negative non-zero `intensity` array, explicit `intensitySemantic`, and explicit
positive finite `wavelength.value` in `angstrom`. The initial release accepts only degree
and Angstrom and performs no inferred or implicit unit conversion.

Point count is 3 to 200,000. Duplicate or unsorted axes, NaN/Infinity, negative or
zero-only intensity, ambiguous units, missing wavelength and oversized inputs are rejected.
No sorting, duplicate merging, URL/path resolution, formula/macro execution or implicit
Cu K-alpha assumption occurs.

DataProfile 2.2 is an additive JSON evolution used only when experimental XRD is present.
It records readiness facts, not detected peaks, matches or phase identity. Versions 2.0
and 2.1 remain readable; generic JSON persistence is sufficient and no backfill or
migration is permitted.

## Parameters

All schemas set `additionalProperties=false`; numeric values must be finite.

| Parameter | Type | Default | Bounds / enum | Meaning |
| --- | --- | --- | --- | --- |
| `normalization` | enum | `max_to_1` | `none`, `max_to_1`, `max_to_100` | presentation normalization only |
| `minimum_prominence` | number | `0.05` | 0 to 1 normalized intensity | detector prominence |
| `minimum_relative_height` | number | `0.0` | 0 to 1 | detector height floor |
| `minimum_peak_separation_deg` | number | `0.10` | 0 to 10 degree 2theta | deterministic separation |
| `max_detected_peaks` | integer | `10000` | 1 to 10000 | detected-peak cap |
| `matching_tolerance_deg` | number | `0.15` | 0.001 to 2.0 degree 2theta | inclusive match bound |
| `max_matching_candidates` | integer | `200000` | 1 to 200000 | candidate-pair cap |
| `max_theoretical_peaks` | integer | `20000` | 1 to 20000 | theory-peak cap |
| `max_output_matches` | integer | `10000` | 1 to 10000 | match cap |
| `max_output_bytes` | integer | `33554432` | 1024 to 33554432 | payload cap |

Resolved defaults and a canonical parameter hash are persisted. Detector parameters are
resolved before theoretical peaks are inspected. No smoothing or background fitting is
supported and no detector parameter is tuned for matching.

## Identity, Units And Wavelength

- Experimental peak identity binds resource hash, detector ID/version, detector parameter
  hash, canonical ordinal and exact detected 2theta.
- The source theory contract has no explicit peak ID, so N3 derives a stable reference ID
  from exact theoretical Artifact checksum, structure identity, canonical peak content and
  duplicate occurrence ordinal. This does not alter or replace `structure.xrd`.
- Match identity binds the N3 parameter hash and both exact peak identities.
- Resource, Artifact, structure, parameter and peak identities use exact equality.
- 2theta/residual unit: `degree`; wavelength: `angstrom`; intensity semantics are
  `counts`, `relative_intensity`, `normalized_relative_intensity`, or
  `arbitrary_relative_unit`.
- Experimental and theoretical wavelengths must agree within `1e-6 angstrom`; mismatch is
  rejected as `XRD_WAVELENGTH_MISMATCH`.

## Detection And Matching

`find_peaks` receives normalized experimental intensity, bounded prominence and height.
A deterministic degree-separation pass orders candidates by descending prominence,
descending intensity, ascending 2theta and source index, retains non-conflicting peaks,
then emits canonical ascending 2theta order.

Matching enumerates tolerance-qualified pairs using sorted peaks and a moving window.
Candidate rows are ordered by absolute residual and exact IDs; a pair is accepted only if
neither peak is already assigned. Matching is position-only and one-to-one. Equal costs
use exact identity order. Unmatched sets are always retained. Zero matches are successful
with null residual statistics.

## Coverage, Errors And Caps

Coverage includes points, detected peaks, theory peaks, matched/unmatched counts and both
matched fractions. Residuals include mean signed, MAE, RMSE, maximum absolute and median
absolute 2theta when matches exist.

Typed detail codes include `EXPERIMENTAL_XRD_MISSING`,
`EXPERIMENTAL_XRD_INVALID_AXIS`, `EXPERIMENTAL_XRD_INVALID_INTENSITY`,
`EXPERIMENTAL_XRD_NON_FINITE`, `EXPERIMENTAL_XRD_TOO_LARGE`,
`XRD_WAVELENGTH_MISSING`, `XRD_WAVELENGTH_INVALID`, `XRD_WAVELENGTH_MISMATCH`,
`THEORETICAL_XRD_MISSING`, `THEORETICAL_XRD_CONTRACT_UNSUPPORTED`,
`THEORETICAL_XRD_CHECKSUM_MISMATCH`, `XRD_PEAK_DETECTION_PARAMETER_INVALID`,
`XRD_PEAK_LIMIT_EXCEEDED`, `XRD_MATCH_TOLERANCE_INVALID`,
`XRD_MATCH_CANDIDATE_LIMIT_EXCEEDED`, `STALE_EXPERIMENTAL_RESOURCE`,
`STALE_THEORETICAL_ARTIFACT`, `FOREIGN_PROJECT_SOURCE`, and `FOREIGN_JOB_SOURCE`.

Caps are 200,000 experimental points, 20,000 theory peaks, 10,000 detected peaks,
200,000 candidate pairs, 10,000 matches, 32 MiB Artifact, 50,000 plot points and 180
seconds. No unbounded assignment matrix is allocated.

## Product And Claim Boundary

Workspace renderer `workspace.experimental-xrd-comparison` consumes only persisted N3
payloads. It provides overlay/table alternatives, matched and unmatched tables, residual
summary, exact peak/match selection and Inspector provenance. Frontend zoom and bounded
display sampling are presentation-only.

Interpretation facts are limited to counts, fractions, approved residuals, selected
peak/match facts, wavelength, tolerance, coverage, warnings and limitations. Report and
Recipe retain source/algorithm/parameter lineage; Recipe is declarative and non-executable.

Required wording is peak correspondence under the stated tolerance. Every delivery surface
must state that this is not Rietveld refinement or definitive phase identification. It may
not claim confirmation, proof, phase purity or structural validity.

## Decisions

`database schema=unchanged`; `migration=unchanged`; migration head
`0007_phase10m1_workspace_domain`; `new public API family=0`; `new dependency=0`;
`lockfile change=0`; `new LLM call sites=0`; `N4 executable task=0`.

Implementation-critical TBD: `0`.
