# Phase 10M-3 Identity Compatibility

Compatibility is exact and deterministic. Every ref carries contract version,
selection kind, source-scope SHA-256, Project identity, and the kind-specific
identity/version/hash fields sealed in Phase 10M-0 and implemented in M1.

The resolver returns `EXACT`, `NOT_APPLICABLE`, `STALE`, or `UNSUPPORTED`.
Project, Job, dataset, dataset-version, Artifact ID/checksum, contract, and
source-reference comparisons are exact. Foreign and stale refs are rejected;
no latest-version rebinding occurs.

Forbidden authority includes array/row/plot/DOM position, display label,
filename, panel title, sort/filter order, visual coordinates, nearest-neighbor
or fuzzy matching, unit guessing, and same-value assumptions. Current Artifacts
that lack formal object IDs are reported as typed unavailable instead of being
upgraded in the browser.

Dataset/ML/composition share `objectId + sampleRef` only when those exact fields
are supplied. Structure, trajectory, phonon, reciprocal, volumetric, evidence,
and claim refs use their sealed fields. M3 performs no scientific derivation.
