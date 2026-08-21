# Qualification Integrity Policy

## Active authority

Qualification integrity is established by content and contract validation:

- explicit authority version and package inventory;
- Case schema, unique Case IDs, and required-file inventory;
- source, provenance, licensing, and direct content inspection;
- byte-for-byte comparison only when protected files are required to remain unchanged;
- deterministic parser, Profile, Intent, Eligibility, parameter-binding, entry-path, and plan-cap validation;
- production tests, runtime checks, and later live Browser evidence.

`QUALIFICATION_INTEGRITY_AUTHORITY = CONTENT_AND_CONTRACT_VALIDATION`.

## Retired qualification digest gates

Qualification-only digest/checksum manifests, digest fields, mismatch counters,
and digest-based pass/fail gates are retired from active authority. New
qualification evidence and any later authority package must not add them.

`HISTORICAL_DIGEST_RECORDS = NON_NORMATIVE`.

`FUTURE_PASS_FAIL_DEPENDS_ON_DIGESTS = NO`.

Historical package archives, legacy evidence, and product runtime integrity
controls are retained as historical or operational records. This policy does
not remove product-level content addressing, artifact provenance, upload
integrity, or other non-qualification security controls.
