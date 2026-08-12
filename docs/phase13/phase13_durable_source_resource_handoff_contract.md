# Phase 13 Durable Source Resource Handoff Contract

Any dataset that can become executable must be reconstructable from durable state without upload-process memory. The exact chain is parsed resource ID -> durable manifest ID -> Profile resource ID -> Eligibility/Planner binding -> fresh-worker resolved ID. PostgreSQL owns scoped identities and manifests; ArtifactStorage owns normalized bytes; Redis owns only bounded queue identity.

The normalized source payload carries a storage checksum distinct from its parser-defined semantic object hash. Both are verified. Missing bytes, checksum mismatch, stale Profile and cross-project keys fail closed. Runtime reparse and latest, fuzzy, filename, display-label or array-position fallback are forbidden.
