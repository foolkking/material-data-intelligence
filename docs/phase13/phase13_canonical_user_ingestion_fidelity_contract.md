# Canonical User Ingestion Fidelity Contract

Canonical semantic coverage and user-ingestion fidelity are separate gates.
Every real-user demo requires a public product action, a sealed input-support
disposition, production parser/normalizer behavior, exact Profile semantics,
durable persistence and Worker resolution. Internal fixture mapping cannot be
counted as a user entry.

The current audit is `6/7`. Demo 5 fails fidelity because phonon YAML/JSON is
`MAPPING_ONLY` and no supported user-visible typed phonon import or selection
path exists. The matrix cannot promote that disposition; reviewer authority is
required either to add bounded input support or revise initial-release Demo 5
scope.

