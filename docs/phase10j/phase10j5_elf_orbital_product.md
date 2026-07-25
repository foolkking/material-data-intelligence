# Phase 10J-5 ELF / Orbital Volumetric Product

Phase 10J-5 adds two application-owned products over the existing
`structure.volumetric_data` artifacts. It does not add a public tool, parser,
canonical volumetric schema, renderer, or dependency.

The ELF product accepts only a supported real scalar
`electron_localization_function` field in `dimensionless` units. The orbital
product accepts only a supported real scalar `orbital_density` field in
`electron/angstrom^3` or `angstrom^-3`. Both preserve the source payload,
field ID/hash, unit, normalization, integral semantics, parser provenance, and
source hash. The application validates decoded values before it presents a
product-specific summary and then reuses the Phase 10J-2 Worker and Three.js
isosurface renderer.

ELFCAR is mapped to source-native ELF without clamping. PARCHG is described as
source-defined partial density because the current canonical contract does not
carry authoritative band, k-point, orbital, occupancy, or energy identity.
CUBE enters the orbital product only through an explicit trusted
`quantity_hint=orbital_density`; generic CUBE remains a generic isosurface and
multi-orbital CUBE remains typed unsupported.

The UI includes exact quantity/unit/isovalue, source and parser identity,
normalization/integral disclosure, range validation, presets, scientific
warnings, field selection, structure overlay, bounded `1x1x1`/`2x2x2`
structure-context replication for periodic sources, clipping, picking,
inspector, and local PNG export. The scalar field itself always remains the
immutable source cell. Non-periodic CUBE does not expose periodic replication.

## Verified Browser Result

Real QueueWorkerRuntime ELFCAR, PARCHG, and explicitly identified CUBE artifact
sets rendered in Chromium, Firefox, and WebKit with WebGL2, one canvas, no
console/page errors, and zero external requests. Chromium additionally closed
the required range-warning, picking, bounded overlay, clipping, PNG, mobile
portrait/landscape, accessibility, and lifecycle cases. The evidence is in
[`evidence/phase10j5_elf_orbital_product/`](evidence/phase10j5_elf_orbital_product/).
