# Phase 10N-3 Experimental XRD Resource Contract

`phase10n3.experimental_xrd_resource.v1` is an inert, strict JSON resource. It requires an exact resource ID/version/hash, `two_theta` in `degree`, wavelength in `angstrom`, equal finite arrays of 3-200,000 points, a strictly increasing axis in `[0, 180]`, non-negative non-zero-only intensity, and one declared intensity semantic. No unit, radiation, sorting, duplicate aggregation, path, URL, formula, macro, HTML or JavaScript inference is allowed.

DataProfile 2.2 is an additive evolution of 2.1. It records readiness facts only; it does not detect peaks, match peaks or assert phase identity. Existing 2.1 profiles remain readable, with no backfill or migration.
