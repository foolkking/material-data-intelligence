# Phase 10H-1 Phonon Band Table

The backend table uses stable q-point-major then branch-major row order and
contains q-point index, segment, reciprocal-fractional q coordinates, path
distance, label, branch index, THz frequency, and the derived
`imaginary`/`near_zero`/`real` classification. Its `units` object identifies
the q-point coordinate system, radian-per-angstrom path distance, and THz
frequency. `max_table_rows` is strict and bounded at 50,000. Truncation is
declared with displayed and total row counts and never changes the canonical
band artifact.

The browser table renders at most 200 rows and explicitly directs users to the
complete canonical JSON. It is keyboard accessible and supplies a caption and
textual units.
