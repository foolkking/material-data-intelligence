# Phase 10I Security, Fixtures, and Evidence

## Trust Boundary

All Phase 10I artifacts are inert JSON. Exact security metadata requires no
JavaScript, HTML, CSS, executable content, external URLs/assets, shaders, or
renderer. Recursive scanning rejects executable keys/markers, URLs, private
paths, excessive depth, and excessive node counts. Numeric values, labels,
provider metadata, transformations, geometry, paths, warnings, and total JSON
size are bounded.

Invalid artifacts return sorted typed errors. Validators handle malformed
numbers and missing topology identities without stack traces or partial
geometry. Artifacts cannot select a module, renderer, shader, material, camera,
worker, iframe, callback, local file, notebook, script, shell command, external
service, or real LLM.

## Caps

The contract caps vertices at 256, edges at 512, faces at 256, vertices per
face at 64, high-symmetry points at 128, variants at 8, segments at 256,
discontinuities at 64, transformations at 8, labels at 64 characters, provider
metadata at 16 KiB, and each JSON artifact at 8 MB. Future adapter reference
search is bounded to generator radius 4 and 728 candidate planes.

## Fixtures and Replay

Fixtures are in `docs/phase10i/fixtures/brillouin_zone_v1/` for simple cubic,
BCC, FCC, hexagonal, triclinic, and a conventional/primitive BCC pair. Evidence
is in `docs/phase10i/evidence/phase10i_brillouin_zone_contract/`.

Replay command:

```powershell
uv run python scripts/generate_phase10i_brillouin_zone_evidence.py
```

The command rebuilds all fixtures and evidence, validates each artifact,
reserializes it twice, compares bytes and SHA-256, independently reconstructs
Voronoi/ConvexHull references, runs negative cases, and emits:

```text
BRILLOUIN_ZONE_CONTRACT_EVIDENCE_PASS
BRILLOUIN_ZONE_INDEPENDENT_REFERENCE_PASS
NO_BRILLOUIN_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

No browser, GPU, API job, planner, or production adapter evidence is claimed.
