# Demo 5: Phonon + Brillouin Zone

## Goal and prompt

> Show the supplied phonon bands and density of states together with the matching Brillouin-zone context.

Prompt SHA-256: `07420478aa73cd79d7a01062600cc46ec6428b98b047f37cfdb9e3fe8ae34a2d`.

## Current user entry

Use the product Data/import surface for each fixture, then enter the prompt in the Planner. Normal users do not supply Tool, Plan, Job, Artifact, Workspace, or storage IDs.

- `docs/phase10h/fixtures/phonon_contract/stable_band.json` | `f8f96c7e93fe67398c15c3dfba7b191c1827bb81d642635f415677da3010883f` | 3562 bytes | `typed_phonon_band_import`
- `docs/phase10h/fixtures/phonon_contract/total_dos.json` | `51dc70e4f4a6b57161606656fc3e2146243101d7793439569763d717e097ae5f` | 1948 bytes | `typed_phonon_dos_import`
- `tests/fixtures/structures/POSCAR` | `80d827271cbda45615d32a17346017d169f51c5eae700f33c6bd0261f948ecda` | 68 bytes | `parse`

## Required semantic coverage

- `phonon.band`
- `phonon.band_dos`
- `phonon.dos`
- `structure.brillouin_zone`

Every selected Tool must be individually eligible. Plan 0.2 is used only for real producer-Artifact-to-consumer dependencies; independent tools may remain Plan 0.1.

## Deterministic reproduction

1. Follow the [clean-checkout setup](README.md#mode-a-deterministic-reproduction).
2. Verify this contract with `uv run python scripts/generate_phase13_3_documentation_reproducibility.py`.
3. Run `uv run python -m pytest -q tests/test_phase13_3_documentation_reproducibility.py`.
4. For service-backed product replay, use the retained Attempt 6 harness and current contract inputs; this package does not create a second E2E authority.

Expected product closure: persisted Artifacts, one Job-derived Workspace, exact typed viewers/Gallery, explicit Report Preview and UI Finalize, and a paired non-executable Recipe.

## Limits and negative boundary

- Values come from supplied/imported phonon data. Generic phonon YAML/JSON remains MAPPING_ONLY; the platform does not calculate phonons.

- Negative: Generic phonon YAML/JSON upload is MAPPING_ONLY and is not auto-promoted.
- This demonstrates current product-path reproducibility. It does not independently validate every numerical output.
