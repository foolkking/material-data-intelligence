# Phase 10N-5 Identity, Units and Provenance

Identity binds resource hash, calculation identity, optional structure hash, Artifact
checksum, spin, k-point, band, DOS channel/projection and parameter hash. Energy is eV;
source unit/reference is retained and Fermi is never inferred. Combined compatibility
requires exact project, calculation/source, optional structure, energy reference and spin,
plus Fermi agreement within `1e-8 eV`. No fuzzy/latest/filename rebinding is allowed.
