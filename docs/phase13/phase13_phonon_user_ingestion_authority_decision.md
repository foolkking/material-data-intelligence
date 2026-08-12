# Phonon User-Ingestion Authority Decision

Decision: `BRANCH_C`.

Attempt 5 used the public `/datasets/upload` action with `stable_band.json`,
`total_dos.json` and `POSCAR`. The phonon JSON files followed `json_limited` and
produced no typed phonon Profile semantics; only the structure was available.
Phase 11 explicitly classifies generic phonon YAML/JSON as `MAPPING_ONLY` with
no generic direct-upload parser.

The repository contains exact phonon schemas, internal normalized mapping,
runtime resolution, Adapters and viewers. It does not contain a normal-user
product route that creates or selects those exact typed resources without
internal IDs or test construction. Therefore Branch A and B are false.

Reviewer options are: authorize a bounded typed phonon import contract, which
changes input support and scope; or revise/defer Demo 5 initial-release scope,
which changes scope but not the Fact Model. This Fix-Forward authorizes neither.

