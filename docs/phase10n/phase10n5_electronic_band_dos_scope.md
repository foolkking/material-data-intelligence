# Phase 10N-5 Scope: Electronic Band Structure + DOS

Status: `REVIEWER_GATE / NOT QUEUED / NOT EXECUTABLE`.

N5 consumes supplied electronic outputs; it does not run DFT. Proposed tools are
`electronic.band_structure`, `electronic.dos` and `electronic.band_dos`. Initial input is
a bounded, strict MSON/JSON subset corresponding to pymatgen BandStructureSymmLine/Dos
semantics. Upstream parser availability does not authorize another file format.

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

Artifacts are Band, DOS, combined Band+DOS, summary and diagnostic contracts. Workspace
has Band, DOS and combined panels with BZ linkage by exact reciprocal identity and
table/text alternatives. Projectors expose supplied-source facts and may say "band gap
derived from the supplied electronic structure". They may not claim experimental
confirmation, GW correction or platform-generated electronic structure.

Caps: 4,096 bands, 65,536 k-points, 262,144 DOS points, two spins, 512 projection channels
and 500,000 display points. Current pymatgen/NumPy/Plotly are sufficient. No Fermi surface,
automatic DFT, VASP/QE execution, remote Materials Project request, new dependency, API,
table or migration is proposed.
