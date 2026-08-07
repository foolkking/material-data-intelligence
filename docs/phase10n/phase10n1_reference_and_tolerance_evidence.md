# Phase 10N-1 Reference And Tolerance Evidence

Reference fixtures are controlled repository structures executed against the locked
pymatgen version. Numeric checks are quantity-specific: periodic images and identities
are exact; distances and weights use documented finite floating-point tolerances;
coordination values use the algorithm's own semantics; canonical ordering and checksums
are exact. Screenshot output is never numeric authority.

Required evidence cases include complete CrystalNN and VoronoiNN runs, periodic-image
retention, algorithm disagreement, invalid/disordered input, stale identity, checksum
rejection, bounded caps and deterministic replay. Runtime evidence is generated from
the focused N1 tests and must be labelled `TEST_FIXTURE`, `RUNTIME_EVIDENCE`,
`BROWSER_EVIDENCE` or `SERVICE_EVIDENCE`; unavailable local services are reported as
unavailable rather than PASS.
