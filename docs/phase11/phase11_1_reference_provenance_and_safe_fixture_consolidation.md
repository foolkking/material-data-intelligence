# Phase 11-1 Reference Provenance + Safe Fixture Consolidation

Phase 11-1 prepares provenance and immutable benchmark inputs for Phase 11-2. It does not validate platform numeric output and does not change production scientific authority.

## Sealed Boundary

The implementation reuses retained repository bytes and records source identity, SHA-256, license disposition, transformation identity, fixture identity/version, and benchmark linkage. No external reference download, scientific API call, notebook, downloaded script, or LLM call was used. Existing fixture bytes are not overwritten.

The actual retained inventory is 46 reference-like records, 170 fixture records, and 55 official/example records. These are repository facts; prompt shorthand counts are not substituted.

## Scientific Honesty

`REFERENCE_READY_FOR_BENCHMARK` means that a typed input is prepared for Phase 11-2. It does not mean `TOOL_VALIDATED`, and no validation level or honest coverage verdict is promoted. Same-library records remain `SELF_REFERENCE`; official-example records with unresolved redistribution status remain `REFERENCE_READY_WITH_REFERENCE_LIMITATION`.

## Handoff

`phase11_2_benchmark_input_manifest.json` has one typed record per Phase 11-0 gap. Every record has a reference, fixture identity/version/checksum, contract-owned tolerance reference, readiness state, and blocking reason or explicit readiness. Phase 11-2 owns all platform-output versus expected-value comparisons.

See the generated [evidence pack](evidence/phase11_1_reference_provenance_safe_fixture/manifest.json), [reference registry](phase11_reference_registry.md), and [fixture registry](phase11_fixture_registry.md).
