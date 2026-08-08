# Phase 10N-3 Artifact Contract

`phase10n3.experimental_xrd_comparison.v1` is produced only by `structure.experimental_xrd_comparison@0.1.0`. It binds the experimental resource hash, exact `structure.xrd@0.1.0` Artifact/checksum and `phase10e4.xrd_pattern.v1`, structure identities, wavelengths, detector/matcher versions and parameter hashes.

The bounded payload contains display series (at most 50,000 points), detected experimental peaks, exact theoretical peak references and hkl metadata, one-to-one matches, both unmatched sets, residuals, coverage, warnings, limitations and provenance. It does not copy the source file, source structure or full theoretical Artifact.
