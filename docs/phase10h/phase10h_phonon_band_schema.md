# Phase 10H Phonon Band Schema

`phase10h.phonon_band.v1` is a closed object containing structure identity, canonical atom order, real lattice, reciprocal/q-point conventions, THz/imaginary policies, explicit q-points and segments, full branch-major frequencies, source-declared degeneracy, ASR metadata, provenance, warnings, and exact security flags.

Structure identity and input provenance hashes are lowercase SHA-256. Species follow canonical atom order and use stable elemental identity. Future eigenvectors and projected DOS must use this same order.

Validation checks exact fields, finite values, lattice conditioning, path distance, `3N`, branch lengths/order, degeneracy membership, caps, warnings, provenance size, and inert content. It does not calculate phonons, infer band connectivity, or correct frequencies.
