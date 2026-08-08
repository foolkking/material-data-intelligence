# Phase 10N-3 Identity, Units and Provenance

Canonical units are degree 2theta and angstrom wavelength; no implicit conversion is implemented. Experimental peak identity binds resource hash, detector/version, detector parameter hash, canonical ordinal and detected position. Theoretical peak identity binds exact theory Artifact checksum, structure identity, canonical peak content and duplicate occurrence. Match identity binds both peak identities and matcher parameter hash.

All hashes and IDs compare exactly. Changes to resource, theory checksum, wavelength, algorithm/version, parameters or tolerance invalidate reuse. hkl remains theoretical metadata and is never represented as definitive experimental indexing.
