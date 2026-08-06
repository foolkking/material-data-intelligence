# Phase 10N-0 Identity, Units, Authority and Wording Seal

## Identity policy

All future N artifacts bind `projectId`, dataset/version, resource/object ID and source
hash, Profile ID/hash, Intent/Eligibility/Plan IDs and hashes, Tool ID/version, ToolCall,
dependency ports, Artifact ID/checksum/contract, and interpretation Claim/Evidence IDs.
No filename, MIME type, label, row position, array index, latest record, nearest point,
or fuzzy match is identity authority.

Structure identity is an immutable canonical structure hash within a dataset resource.
Site identity is a stable site reference bound to that structure hash, species/occupancy,
fractional coordinates and source hash. A site index may be used only inside that exact
immutable structure hash and is never cross-version identity.

Periodic neighbor identity is central site + neighbor site + periodic image vector,
distance, weight, algorithm ID/version and parameter hash. Trajectory identity is
trajectory ID/hash + frame ID/time + atom ID and species/cell binding. Experimental XRD
identity is source ID/hash + wavelength + axis/unit + normalized intensity + peak parameter
hash + peak ID. Electronic identity is source/calculation ID/hash + spin + k-point/path
identity + band/channel/projection identity + energy reference.

## Canonical units proposal

| Quantity | Internal unit | Missing/ambiguous behavior |
| --- | --- | --- |
| distance | angstrom | reject; no silent conversion |
| fractional coordinate | dimensionless in declared lattice basis | reject if lattice absent |
| angle / XRD 2theta | degree | reject mixed axis units |
| coordination / neighbor weight | dimensionless | preserve algorithm semantics |
| wavelength | angstrom | reject absent wavelength for N3 |
| intensity | source-declared normalized dimensionless | retain normalization provenance |
| RDF radius | angstrom | reject unitless input |
| RDF value | dimensionless | record normalization policy |
| time | picosecond | reject missing time unless an explicit phase policy permits step-only display |
| MSD | angstrom^2 | record unwrapping and correction policy |
| diffusion coefficient | angstrom^2 / picosecond | emit only with fit diagnostics |
| electronic energy/Fermi energy | electronvolt | reject missing reference when classification needs it |
| DOS | states / electronvolt with declared normalization basis | preserve source normalization |
| reciprocal coordinate/k-path distance | reciprocal-lattice coordinates / inverse angstrom | bind to exact reciprocal lattice |

Conversions must be server-side, deterministic, tested, and recorded in Artifact
provenance. Browser-only conversion and silent mixed-unit merges are prohibited.

## Scientific wording

Allowed wording is algorithm-qualified: `algorithm-derived local coordination`,
`coordination under stated algorithm and parameters`, `peak correspondence under stated
wavelength, preprocessing and tolerance`, `MSD computed under the stated unwrapping and
identity policy`, `estimated diffusion coefficient over the selected fit window`, and
`band gap derived from the supplied electronic structure`.

Forbidden wording includes true chemical bond, definitive bonding, phase is proven,
experimental confirmation, stable bulk diffusion coefficient, diffusive regime confirmed,
GW-corrected result, or ground-state electronic structure produced by the platform.

## Authority and security

Adapters compute; Artifacts persist; projectors expose bounded facts; interpretation is
grounded narrative; Report composes. No future proposal moves authority into the browser,
Workspace, Report, Recipe, LLM, or untrusted payload. Untrusted numeric/text input is
finite, size-bounded, duplicate-key rejected, prototype-key rejected, and inert.
