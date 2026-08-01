# Phase 10L-5 Evidence Contracts

The Python contracts and checked-in JSON schema are:

* `NaturalLanguageEvidenceCase 1.0`;
* `NaturalLanguageEvidenceRun 1.0`;
* `DeepSeekVerificationRecord 1.0`;
* `DeepSeekVerificationSuite 1.0`;
* `Phase10LClosureManifest 1.0`.

All contracts reject unknown fields, duplicate JSON keys, non-finite numbers,
excessive nesting, and oversized serialized content. Semantic IDs and hashes
exclude runtime timestamps. A per-case verification record is capped at twelve
real calls. The current-product suite records five cases and 16 calls; the
supplemental historical replay records 40 additional cases and 92 calls.
These are separate bounded records and neither weakens the per-case cap.

The closure manifest uses LF-normalized UTF-8 text hashing and raw PNG hashing.
It includes the exact case captures, live run records, historical replay
records, provider audits,
sanitized failed-attempt provenance, browser audit, screenshots, and replay
metadata. It never includes provider payloads, authorization headers, keys, or
private paths.
