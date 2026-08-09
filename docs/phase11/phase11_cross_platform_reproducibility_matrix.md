# Phase 11 Cross-Platform Reproducibility Matrix

The authoritative input is `phase11_3_reproducibility_input_manifest.json`. It admits P11B-001, 002, 003, 004, 005, 008, 010, and 011. Each case must preserve exact benchmark/reference/fixture/tolerance identities and units on Linux and Windows.

The implementation CI publishes separate platform replay artifacts and a cross-platform matrix. All eight records are invariant-only; numeric value comparison is `NOT_APPLICABLE`, not an inferred pass.

