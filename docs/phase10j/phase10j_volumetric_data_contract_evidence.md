# Phase 10J Volumetric Data Contract Evidence

## Location

Evidence is committed under
`docs/phase10j/evidence/phase10j_volumetric_data_contract/`; source fixtures are
under `docs/phase10j/fixtures/volumetric_contract/`.

## Generation

```bash
uv run python scripts/generate_phase10j_volumetric_evidence.py
```

The generator uses only Python standard-library JSON, SHA-256, `struct`, gzip,
zlib, and math support plus the local contract implementation. It emits:

```text
VOLUMETRIC_DATA_CONTRACT_EVIDENCE_PASS
NO_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

## Captures

* `schema/schema_snapshots.json`: five schema IDs, caps, storage order, and
  inert security declaration.
* `validation/fixture_validation.json`: periodic, triclinic, affine, binary,
  and chunk validation results.
* `references/independent_math.json`: independent little-endian decoder,
  flatten order, affine center, triclinic coordinate, and integrals.
* `replay/determinism.json`: serialized replay hashes.
* `security/negative_cases.json`: dimensions, mixed boundary, singular basis,
  non-finite values, traversal, truncation, and endpoint rejection.
* `security/audit.json`: no executable content or external resource and bounded
  decompression/allocation.
* `artifact_hashes.json`: byte length and SHA-256 of every fixture/evidence
  file except the inventory itself.

The test `tests/test_phase10j_volumetric_evidence.py` independently reloads the
committed outputs, validates binary payloads/datasets/manifests, decodes raw
float64 bytes with `struct`, checks scientific semantics, verifies every file
hash, and AST-audits the contract for network/deserialization/execution imports
or calls.

## Scope Boundary

The evidence is contract evidence, not parser, adapter, API, browser, GPU,
renderer, slice, or isosurface evidence. No dependency or lockfile is changed.
