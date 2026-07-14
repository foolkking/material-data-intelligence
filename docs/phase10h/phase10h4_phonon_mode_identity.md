# Phase 10H-4 Mode Identity

`phase10h.phonon_mode_ref.v1` binds a mode to the band artifact ID/SHA-256,
structure identity, calculation identity, q-point index/coordinates/segment,
source-stable branch index, frequency, reciprocal convention, and NAC direction.
`mode_id` is the SHA-256 of band hash, q-point index, branch index, and NAC
direction. Frequency, labels, filenames, and UI indices are not identities.

Changing the band content changes the mode ID. A stale hash or mismatched bound
field is rejected as `PHONON_MODE_REFERENCE_STALE` or a typed binding error.
