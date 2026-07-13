# Phase 10H Evidence

Evidence lives in [`evidence/phase10h_phonon_contract/`](evidence/phase10h_phonon_contract/). It contains schema snapshots, reciprocal/frequency/imaginary/branch/degeneracy/DOS/compatibility/cap policies, valid and invalid fixture results, independent NumPy/SciPy physics comparison, actual TypeScript/Python validation comparison, deterministic hashes, and security/network audits.

Regenerate in this order:

```powershell
uv run python scripts/generate_phase10h_phonon_contract_evidence.py
Set-Location apps/web
npm exec -- vite-node test/phonon-contract-evidence.ts
Set-Location ../..
uv run python scripts/generate_phase10h_phonon_contract_evidence.py --hash-only
```

Expected markers include `PHASE10H_PHONON_CONTRACT_EVIDENCE_PASS`, `PHONON_CONTRACT_CROSS_LANGUAGE_EVIDENCE_PASS`, `NO_EXTERNAL_NETWORK_REQUESTS`, and `NO_SECRET_PATTERN_HITS`.
