# Phase 10J-5 Security and Evidence

The trust boundary remains artifact JSON/binary -> canonical frontend
validation -> allowlisted product mapper -> bounded payload loader -> static
application Worker -> application Three.js renderer. Artifact values cannot
provide JavaScript, Worker/WASM, shader, HTML/CSS, module path, URL, texture,
normalization expression, orbital combination, or callback.

Product caps retain the Phase 10J-2 payload/voxel/mesh/GPU/layer budgets and add
bounded product metadata and a maximum of eight structure-overlay replicas.
The overlay derivation caps displayed atoms at 4096 and bonds at 8192, uses
only validated lattice vectors, and leaves non-periodic sources unreplicated.
Hidden atoms and hidden surfaces are now excluded from raycasting. Artifact
switches and overlay rebuilds dispose the old engine before creating one new
canvas/context.

Evidence uses committed small fixtures and real Mock Planner -> planner job ->
QueueWorkerRuntime -> adapter -> artifact storage execution. It includes real
gzip float64 payloads for ELFCAR, PARCHG, and explicitly identified CUBE, plus
synthetic test-only range and generic/signed boundary cases. Browser requests
are restricted to the local production frontend and mocked local job API.

Verified markers:

```text
ELF_ORBITAL_RUNTIME_EVIDENCE_PASS
ELF_ORBITAL_PRODUCT_BROWSER_EVIDENCE_PASS
ELF_ORBITAL_PRODUCT_RANGE_EVIDENCE_PASS
ELF_ORBITAL_PRODUCT_IDENTITY_EVIDENCE_PASS
ELF_ORBITAL_PRODUCT_PERFORMANCE_EVIDENCE_PASS
NO_ELF_ORBITAL_PRODUCT_EXTERNAL_NETWORK_REQUESTS
NO_SECRET_PATTERN_HITS
```

No dependency or lockfile changed. The configured npm audit endpoint remains a
separate repository limitation and must not be reported as clean when it is
unavailable.
