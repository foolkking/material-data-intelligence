# Phase 10I High-Symmetry Path and Provider Policy

## Separation from Geometry

`phase10i.kpath.v1` is optional and independent from
`phase10i.brillouin_zone.v1`. The first BZ comes only from the primitive
reciprocal lattice. A k-path is a provider/convention result and cannot alter
vertices, faces, or reciprocal basis identity.

## Points and Labels

Each point records a stable content-derived ID, canonical label key, safe plain
text display label, sorted aliases, reciprocal-fractional and Cartesian
coordinates, basis role, and provider identity. Coincident labels within the
fixed coordinate tolerance merge deterministically while retaining all source
label keys. Labels cannot contain HTML, script markers, URLs, paths, callbacks,
or arbitrary expressions.

## Variants and Discontinuities

One to eight explicit path variants may be recorded, with exactly one selected.
Each variant contains an ordered list of stable segment IDs. Segments record
both endpoint identities, provider branch identity, Cartesian reciprocal length,
and cumulative start/end distance. Branch changes are explicit discontinuities;
no distance jump is added. Path geometry is never inferred from a label string.

## Provider Policy

Provider metadata is allowlisted and records name, version, path convention,
input structure hash, `symprec` in angstrom, angle tolerance in degrees,
standardization status, warnings, and whether time reversal was used. Current
contract fixtures use `internal_fixture_reference`; future local producers may
use approved `pymatgen_highsymmkpath`, `seekpath`, or `spglib` identities.

Network providers, arbitrary plugin names, free-form policy strings, magnetic
path conventions, and undeclared time-reversal behavior are rejected. Provider
warnings do not relax geometry or schema validation.
