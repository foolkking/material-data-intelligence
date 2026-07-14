# Phase 10H-4 Evidence

Evidence is stored in
`docs/phase10h/evidence/phase10h4_phonon_eigenvector_contract/`. It contains
schema snapshots, policy records, small valid/invalid fixtures, global-phase and
mass-weighting references, NumPy non-Gamma comparison, deterministic hashes,
cross-language validation, security, and network records.

Replay:

```powershell
uv run python scripts/generate_phase10h4_phonon_eigenvector_evidence.py
uv run python -m pytest -q tests/test_phase10h4_phonon_eigenvector_contract.py
npm --prefix apps/web test -- --run app/lib/phononEigenvectorContract.test.ts
```
