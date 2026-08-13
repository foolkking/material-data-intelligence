# Demo 7: Electronic Band + DOS

## Goal and prompt

> Inspect the supplied electronic band structure and DOS, including gap, spin, projection and compatibility limitations.

Prompt SHA-256: `aedbb3c41c4eabf8de863973e454562c51ee4361bfe35d89eaba54656a75993f`.

## Current user entry

Use the product Data/import surface for each fixture, then enter the prompt in the Planner. Normal users do not supply Tool, Plan, Job, Artifact, Workspace, or storage IDs.

- `docs/phase10n/evidence/phase10n5_electronic_band_dos/electronic_resource_contracts/band.json` | `51fd7a057a398eaa127917338030da3dccb15f5fcd8f299822c76d741e11c6c4` | 1808 bytes | `parse`
- `docs/phase10n/evidence/phase10n5_electronic_band_dos/electronic_resource_contracts/dos.json` | `b0023d82aa1448893def37f3a323de22a642e7c4f048737dd373ea0342aebbdf` | 1101 bytes | `parse`

## Required semantic coverage

- `electronic.band_structure`
- `electronic.dos`

Every selected Tool must be individually eligible. Plan 0.2 is used only for real producer-Artifact-to-consumer dependencies; independent tools may remain Plan 0.1.

## Deterministic reproduction

1. Follow the [clean-checkout setup](README.md#mode-a-deterministic-reproduction).
2. Verify this contract with `uv run python scripts/generate_phase13_3_documentation_reproducibility.py`.
3. Run `uv run python -m pytest -q tests/test_phase13_3_documentation_reproducibility.py`.
4. For service-backed product replay, use the retained Attempt 6 harness and current contract inputs; this package does not create a second E2E authority.

Expected product closure: persisted Artifacts, one Job-derived Workspace, exact typed viewers/Gallery, explicit Report Preview and UI Finalize, and a paired non-executable Recipe.

## Limits and negative boundary

- Band/DOS values and Fermi energy are source supplied. Unknown energy units are ineligible; classification is policy-bounded.

- Negative: Unknown energy units are INELIGIBLE and are never assumed to be eV.
- This demonstrates current product-path reproducibility. It does not independently validate every numerical output.
