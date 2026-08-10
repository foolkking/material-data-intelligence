# Phase 11-4 Honest Coverage Seal

Phase 11-4 classifies the existing Tool, input, and official-example evidence. It does not create
scientific truth, change a parser support verdict, promote a validation level, or acquire a reference.

## Authority

The live Registry is the source for the 62 Tool rows. Existing Phase 11-0 matrices provide input and
official-example rows. Phase 11-3 provides eight retained `PASS_INVARIANT` cases after implementation
CI; those cases contain no numeric cross-platform claim. Coverage is a separate axis from validation
level, input support, browser status, and service status.

The coverage taxonomy is frozen as `DIRECT_VERIFIED`, `OFFICIAL_DERIVED_VERIFIED`, `REFERENCE_VERIFIED`,
`MAPPING_ONLY`, `EXTRACTION_REQUIRED`, `FUTURE_SCOPE`, and `UNSUPPORTED`.

## Results

- Tool rows: 62, unique and classified exactly once.
- Input rows: 14, with support verdicts preserved from Phase 11-0.
- Official/example rows: 55, retained records classified without treating mapping as verification.
- Tool coverage: 62 `MAPPING_ONLY`; no Tool was promoted to independent numeric coverage.
- Input coverage: 10 `DIRECT_VERIFIED` for input-path evidence, 1 `MAPPING_ONLY`, and 3 `UNSUPPORTED`.
- Official/example coverage: 55 `MAPPING_ONLY`.
- Phase 11-2: 12 benchmark records, 8 `PASS_INVARIANT`, 4 `NOT_APPLICABLE`, 0 failures.
- Phase 11-3: 8 admitted cases, Linux/Windows invariant replay passed in CI, numeric cross-platform status remains `NOT_APPLICABLE`, V4 remains 0.

`DIRECT_VERIFIED` on an input row means that the platform ingestion path was directly exercised. It does
not mean that every scientific result produced from that input has an independent reference.

## Explicit Limits

Browser screenshots, service persistence, fixtures, internal regression, and mapping records are not
independent scientific numeric references. Self-reference is not independent cross-library validation.
The Phase 11-5 closure gate remains reviewer-gated; this document does not mark Phase 11 complete.

Machine-readable matrices and hashes are retained under
`docs/phase11/evidence/phase11_4_honest_tool_input_example_coverage/`.
