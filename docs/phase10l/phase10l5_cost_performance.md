# Phase 10L-5 Cost and Performance

The live gate is bounded per case at twelve calls. The current passing suite
used 16 calls total: 3 dataset, 3 structure, 3 ML, 4 phonon, and 3 volumetric.
Token usage and elapsed time are recorded per provider call without raw
content. Provider timeout and output caps remain those of `DeepSeekProvider`.

The supplemental historical replay is independently bounded and used 92 real
calls across 40 cases. Together the two acceptance records cover 45 semantic
cases with 108 real calls. These measurements are evidence costs, not a
production throughput claim.

Default CI never calls a real provider. Deterministic evidence generation and
browser replay are bounded by the five current cases plus three typed non-ready
captures, Profile caps,
evidence caps, and Playwright capture budget. Evidence manifests record byte
sizes and hashes; repeated deterministic replay is compared semantically.

The live suite is an acceptance gate, not a production throughput benchmark.
