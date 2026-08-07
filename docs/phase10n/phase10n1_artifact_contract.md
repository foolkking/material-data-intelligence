# Phase 10N-1 Artifact Contract

Two production artifact discriminators are implemented:

| Artifact | Schema | Producer |
| --- | --- | --- |
| CrystalNN coordination | `phase10n1.crystalnn_coordination.v1` | `structure.coordination_crystalnn@0.1.0` |
| VoronoiNN coordination | `phase10n1.voronoinn_coordination.v1` | `structure.coordination_voronoinn@0.1.0` |

Each table payload records algorithm and library versions, resolved parameters and
parameter hash, exact source/structure identity, per-site results, neighbor identities,
periodic images, distances, weights where defined, coverage, warnings, unsupported site
reasons, diagnostics, provenance and security flags. Summary Markdown, canonical JSON
and declarative Recipe artifacts are derived from the same result. Payloads are inert:
no HTML, JavaScript, module, iframe, URL or executable authority is accepted.

Generic artifact persistence, checksum storage and MinIO retrieval are reused. No new
table, column or migration is required.
