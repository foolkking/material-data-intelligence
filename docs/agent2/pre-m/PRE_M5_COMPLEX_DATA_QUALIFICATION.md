# Pre-M5 Complex Material Data Qualification

Status: `PASS_WITH_EXPLICIT_LIMITS`  
Date: 2026-09-11

Pre-M5 qualifies the current supported contracts; it does not raise caps or
claim a production-scale scholarly/data warehouse.

## Qualification tiers

```text
S = small reference
R = representative
H = near a current validated cap
X = beyond cap; typed rejection/fallback is success
```

Existing family qualification fixtures cover S/R and selected H/X boundaries.
This run re-executed current family contracts and frontend presentation tests;
it did not generate every possible maximum-size Cartesian combination.

## Current supported envelope

| Area | Current authoritative limit / presentation boundary |
|---|---|
| Upload | 8 files; 64 MiB/file; 128 MiB/submission |
| Stored Artifact | 256 MiB absolute storage cap; family/viewer caps may be lower |
| Dataset explorer | 100,000 rows; 512 columns; 64 properties; 256 categories/structures; 5,000 atoms/structure; 200 linked rows; 8,000,000-byte family Artifact |
| Canonical trajectory | 4,096 atoms; 10,000 frames; 12,000,000 coordinate values; 64,000,000-byte JSON |
| Trajectory analyses | 200 frames; 5,000 atoms; 2,000,000 RDF pair evaluations; 2,048 bins/lags; 4,096 origins/lag; 10,000 fit points; 32 MiB output |
| Structure scene | 256 sites; 2,048 bonds; 32 species; 1,000,000-byte scene; bounded compatible supercell projections |
| Phonon | 512 atoms; 1,536 branches; 4,096 q-points; 100,000 DOS points; 512 projections; 4,000,000 numeric values; 64,000,000-byte Artifact |
| Electronic | 65,536 k-points; 4,096 bands; 2 spins; 1,024 segments; 4,000,000 band values; 262,144 DOS points; 512 projections; 4,000,000 DOS values; 64 MiB output |
| Volumetric | canonical contract 512 per dimension and 16,777,216 voxels; current public parser 2,097,152 voxels; 8 fields; 512 MiB dataset; browser direct-volume path has stricter device/payload limits |
| Workspace / Report | 32 panels; bounded selected Report sources; one active heavy viewer lease |
| Context | operation-specific bounded policies; current effective provider input budgets remain below the provider window and literature competes with direct Result evidence |

## Integrity requirements

- no silent source truncation or computation sampling;
- every bounded table/plot discloses the denominator or typed cap;
- X cases reject/fallback explicitly;
- presentation samples never become scientific inputs;
- canonical Result/Artifact/source data remain unchanged.

## Verification and limitations

Current complex-family production tests (excluding immutable historical
evidence-manifest byte assertions) pass `380 passed, 1 skipped`. The excluded
historical assertions compare stored raw byte lengths against files whose
line endings were converted to CRLF by the Windows checkout; historical
scientific content was not modified to force a green result.

M owns sustained duration/load/failure behavior: leases/checkpoints, worker
crash recovery, queue fairness/backpressure, multi-hour large-payload transport
and systematic high-load fault qualification.
