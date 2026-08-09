# Phase 11 Variance and Reproducibility Policy

Phase 11-3 uses exactly five verdicts:

```text
EXACT
TOLERANCE_BOUNDED
DISPLAY_ONLY_VARIANCE
UNSUPPORTED_PLATFORM
KNOWN_LIMITATION
```

The primary scientific environment is the current lockfile environment. Linux CI and Windows, the primary development/runtime platform, form the minimum OS matrix. macOS is `NOT_CURRENT_RELEASE_TARGET` unless repository support is separately established.

The audit covers floating point behavior, negative zero, NaN/Inf rejection, hash serialization, JSON ordering, locale, timezone, random seeds, PCA sign convention, KMeans seeds, assignment ties, ConvexHull ordering, neighbor ordering, spglib behavior, reciprocal-path ordering, browser plot ordering, and GPU/WebGL display variance.

Browser comparison is invariant-based, not pixel-perfect scientific equality. Presentation variance cannot alter persisted scientific values.
