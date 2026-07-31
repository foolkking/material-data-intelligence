# Phase 10L-4 Caps and Performance

Hard caps include 16 approved projected source Artifacts, 128 unsupported
Artifact audit entries, 256 evidence items, 32 claims, eight
evidence refs per claim, 128 warnings, 64 limitations, 262,144 provider/bundle
bytes, 131,072 interpretation bytes, and JSON depth 14. Oversized unsafe
projection returns `EVIDENCE_CAP_EXCEEDED`; it is not silently truncated.

Current local near-cap evidence exercises 256 evidence items and reports
serialized bytes, elapsed time, and traced peak memory in
`evidence/phase10l4_grounded_interpretation/performance_audit.*`. These fixture
measurements are bounded regression evidence, not a production capacity claim.
