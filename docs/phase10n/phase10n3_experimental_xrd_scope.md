# Phase 10N-3 Scope: Experimental XRD Comparison + Peak Matching

> N3-R0 authority correction: the approved Tool is exactly
> `structure.experimental_xrd_comparison@0.1.0`. Detection, normalization and matching
> are internal Adapter components, not Registry Tools. Existing `structure.xrd` /
> `phase10e4.xrd_pattern.v1` is the only theoretical authority. Exact contracts are
> sealed in `phase10n3_r0_contract_closure.md`; older candidate Tool IDs below are
> historical proposals and are not executable authority.

Status: `REVIEWER_GATE / NOT QUEUED / NOT EXECUTABLE`.

N3 distinguishes existing theoretical XRD generation from a new bounded experimental
pattern resource and comparison. Proposed tools are `xrd.experimental_pattern` and
`xrd.peak_match`; theoretical peaks come from the exact existing `structure.xrd`
Artifact through AnalysisPlan 0.2.

Input requires experimental 2theta and intensity arrays, axis/intensity units,
wavelength and source ID/hash, with optional declared preprocessing metadata. Defaults
are: max-normalization only; no baseline removal or smoothing unless explicitly selected;
SciPy `find_peaks` with explicit prominence/separation; deterministic one-to-one minimum
delta matching within explicit tolerance, stable tie-break by peak IDs; reject wavelength
mismatch and disclose nonoverlapping ranges.

Artifacts contain normalized patterns, detected experimental peaks, theoretical hkl
peaks, matched pairs, delta 2theta, unmatched sets, coverage, residual summary, parameters,
units, warnings and provenance. Peak IDs derive from source/policy hashes and stable
numeric identity, never sorted-array position alone.

Workspace uses overlay and peak/match tables with text alternatives. Interpretation may
say "peak correspondence under the stated wavelength, preprocessing and tolerance". It
may not confirm a phase or structure.

Caps: 32 MiB, 200,000 points, 20,000 theoretical peaks, 10,000 detected peaks and 10,000
matches. No Rietveld/structure/phase-fraction refinement, phase search, phase
identification or external service. Existing NumPy/SciPy/pandas/Plotly are sufficient;
no new dependency, API, table or migration is proposed.
