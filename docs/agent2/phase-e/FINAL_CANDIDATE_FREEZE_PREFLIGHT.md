# FINAL CANDIDATE FREEZE PREFLIGHT

- Phase: FINAL_CANDIDATE_FREEZE_PREFLIGHT
- Active repository: `E:\1project\mdi-b0-5a1`
- Base HEAD: `2727e94ba6adaaf0c6ff9914f8137d130b34c777`
- Historical Phase D candidate: `54c66abc499c646dc27b612dbf28747b176177c8` (historical only)
- Frozen authority package SHA256: `3fa4038b3c5a33bec70d5577a3dd93411c6347d55cb99fd721d6948036a70952`

## Mandatory stop conditions

1. Do not start Phase E, services, namespace, canonical fixtures, cases, provider calls, or the 16-case matrix.
2. Do not reset, clean, checkout, commit, push, tag, or release. Preserve all current uncommitted work.
3. Restore the exact frozen qualification package to the active authority path and verify byte/hash equality.
4. Determine whether M3 is externally closed. M3-007 retrying-UI truthfulness remains open unless a later externally accepted M3 attempt exists; Phase E cannot substitute for M3 acceptance.
5. Classify every changed/untracked path with no unknowns; trace final runtime/frontend/migration files to owner and evidence; identify exclusions.
6. Inventory migrations, compute a final-candidate diff fingerprint, run safe pre-freeze regression and read-only canonical service checks.
7. Produce a commit proposal only. `COMMIT_EXECUTED = NO`; Phase D re-seal and Phase E remain unexecuted.

## Required outputs

Create a fresh qualification evidence directory containing:
`AUTHORITY_PACKAGE_RESTORATION.json`, `M3_DEPENDENCY_CHECK.json`, `FINAL_CANDIDATE_PATH_CLASSIFICATION.json`, `FINAL_CANDIDATE_EXCLUSIONS.json`, `FINAL_PRODUCTION_FILE_PROVENANCE.json`, `MIGRATION_INVENTORY.json`, `FINAL_CANDIDATE_DIFF_MANIFEST.json`, `FINAL_CANDIDATE_PREFREEZE_TESTS.json`, `CANONICAL_SERVICE_HEALTH_READONLY.json`, `FINAL_CANDIDATE_COMMIT_PROPOSAL.md`, raw git snapshots, and integrity hashes.

## Stop result

If M3-007 is still not externally accepted, return `STATUS = BLOCKED`, preserve `CANONICAL_CASES_EXECUTED = 0/16`, `REAL_LLM_CALLS = 0`, and set `NEXT ACTION = FIX_PRECOMMIT_BLOCKER`.
