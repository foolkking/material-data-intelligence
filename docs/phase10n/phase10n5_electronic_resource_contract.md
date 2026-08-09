# Phase 10N-5 Electronic Resource Contract

Strict resources are `phase10n5.electronic_band_resource.v1` and
`phase10n5.electronic_dos_resource.v1`. Both bind resource ID/version/hash, calculation
identity, optional formal structure identity, eV, source or Fermi reference, optional
explicit Fermi energy, and non-spin-polarized or up/down spin mode. Unknown keys,
non-finite values, unsupported SOC/noncollinear semantics and cap overflow are rejected.
Band resources preserve fractional reciprocal coordinates, exact k-point/band IDs, path
segments/breaks, energies and optional occupations. DOS resources preserve a monotonic
grid, explicitly supplied total channels, unit semantic, projections and completeness.
