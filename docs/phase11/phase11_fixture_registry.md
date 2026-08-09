# Phase 11 Fixture Registry

Phase 11-1 reuses 170 retained fixture records without rewriting bytes. Each record has an immutable fixture ID/version, source and normalized SHA-256, path, format, source-qualified units, disposition, and benchmark handoff. The identity transformation `P11TRANS-IDENTITY-001` is metadata registration only and has no numeric, unit, or ordering mutation.

Authoritative fixture replacement is prohibited. Any future source, transformation, schema, unit, or expected-content change requires a new fixture version and a new checksum.
