# Phase 10H-3 Source Lineage

Compatibility uses canonical calculation lineage, input hash, force-constants
identity when present, NAC metadata, and cell relation. Strict product mode
rejects contradictions. Missing optional lineage can only produce the bounded
`PHONON_BAND_DOS_LINEAGE_INCOMPLETE` warning when required identities pass.

The product does not claim to produce force constants, run phonopy/DFPT, or
establish provenance from filenames.
