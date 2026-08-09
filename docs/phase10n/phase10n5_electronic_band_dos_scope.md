# Phase 10N-5 Scope: Electronic Band Structure + DOS

Status: `AUTHORIZED / N5-R0 CONTRACTS FROZEN / IMPLEMENTATION IN PROGRESS`.

N5 consumes supplied electronic outputs; it does not run DFT. Exact Tools are
`electronic.band_structure@0.1.0` and `electronic.dos@0.1.0`. Combined Band+DOS is a
deterministic compatible-Artifact presentation with Tool count zero. Inputs are bounded,
strict `phase10n5.electronic_band_resource.v1` and
`phase10n5.electronic_dos_resource.v1` JSON resources.

Band identity binds source/calculation hash, spin, reciprocal lattice/path, k-point ID,
band ID and energy reference. DOS identity binds spin, energy grid, channel and optional
element/orbital projection completeness. Internal energy is eV. Missing Fermi level is
allowed for source-referenced plots only; gap/classification is unavailable unless a
declared reference exists.

Line-mode and mesh data are separate contract modes. Direct/indirect gap policy,
metal/semiconductor threshold, spin combination, duplicated path endpoints, band indexing,
DOS normalization basis and smearing metadata are explicit. Initial release includes
total DOS and formally complete element/orbital DOS projections under the proposed
completeness contract. Projected bands remain Future Scope.

Scientific Artifacts are `phase10n5.electronic_band_structure.v1` and
`phase10n5.electronic_dos.v1`; there is no combined scientific Artifact. Workspace
has Band, DOS and combined panels with BZ linkage by exact reciprocal identity and
table/text alternatives. Projectors expose supplied-source facts and may say "band gap
derived from the supplied electronic structure". They may not claim experimental
confirmation, GW correction or platform-generated electronic structure.

Caps: 4,096 bands, 65,536 k-points, 4,000,000 band values, 262,144 DOS points, two spins,
512 projection channels, 4,000,000 DOS values, 64 MiB output and 500,000 display points.
Current pymatgen 2026.5.4, NumPy 2.4.6 and SciPy 1.17.1 are sufficient. No Fermi surface,
automatic DFT, VASP/QE execution, remote Materials Project request, new dependency, API,
table or migration is proposed.

DataProfile evolves additively from 2.3 to 2.4 only for deterministic readiness. Gap
algorithm `mdi.supplied_band_gap_scan@1.0.0` uses complete supplied occupations, otherwise
an explicit Fermi energy. Ties sort by spin, k-point ID and band ID. A Fermi crossing or
sampled gap at most `1e-5 eV` is `METAL_LIKE_UNDER_POLICY`; a larger sampled gap is
`NONZERO_GAP_UNDER_POLICY`. Total DOS must be supplied. Projection completeness is exactly
`COMPLETE`, `PARTIAL` or `UNKNOWN`; projections are never summed to invent total DOS.
