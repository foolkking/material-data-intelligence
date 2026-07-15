# Phase 10I-1 Brillouin Zone Adapter

## Outcome

`structure.brillouin_zone` is the single registered data-generation tool for
the Phase 10I contract family. It accepts exactly one ordered, non-magnetic,
three-dimensional periodic `Structure`, runs through the existing validated
AnalysisPlan and QueueWorkerRuntime path, and emits six inert artifacts:

1. `reciprocal_lattice.json`
2. `brillouin_zone.json`
3. `kpath.json`
4. `brillouin_zone_manifest.json`
5. `summary.md`
6. `recipe.json`

The adapter does not contain or authorize a Three.js/WebGL renderer. An
application-owned `BrillouinZoneJsonPreviewPanel` displays fixed reciprocal,
BZ, k-path, and manifest tabs plus React-escaped raw JSON. It is the only new
frontend consumer in this phase and creates no canvas or graphics context.

## Input and Parameters

Input is one normalized `pymatgen.Structure`. Collections, non-structure
objects, empty structures, partial occupancy/disorder, nonzero magnetic
moments, explicit dimensions other than three, singular/ill-conditioned
lattices, and structures above 512 sites are rejected before artifacts are
written.

Parameters are closed to required reciprocal/BZ/k-path output flags, the
`contract_default` standardization and k-path provider, time reversal enabled,
the versioned symmetry and angle tolerances, and alternative variants disabled.
Unknown fields, disabled required outputs, non-finite/out-of-range tolerances,
unapproved providers, and magnetic/time-reversal variants are rejected.

## Provider and Mathematics

The dependency decision uses only packages already installed by the project:

- `pymatgen 2026.5.4` `SpacegroupAnalyzer` with
  `international_monoclinic=False`, matching the selected path convention;
- installed `spglib 2.7.0` through pymatgen symmetry analysis;
- pymatgen reciprocal Wigner-Seitz geometry;
- `HighSymmKpath(path_type="setyawan_curtarolo")`;
- NumPy finite matrix inversion for the explicit source-to-standardized-
  primitive transformation.

No `seekpath`, new dependency, external API, remote structure lookup, notebook,
or script execution was introduced. Real/reciprocal vectors remain rows and the
contract formula remains `B=2*pi*(A^-1)^T`.

## Geometry and Path Mapping

The adapter obtains a standardized primitive and conventional cell, records
`A_new=M*A_old` when the source and primitive bases differ, and builds the
canonical reciprocal contract before geometry. Each pymatgen Wigner-Seitz face
is bound to an integer reciprocal generator by an exhaustive bounded
`[-4,4]^3` search (728 nonzero candidates) and a deterministic
residual/norm/lexicographic tie-break. The unchanged Phase 10I canonicalizer
then owns vertex merging, face winding, edges, incidence, generator planes,
volume, Euler, manifold, convexity, central symmetry, caps, and hashes.

Provider labels are normalized to bounded application-owned ASCII keys;
`\\Gamma` becomes key `GAMMA` with display label `Γ`. The adapter emits one
selected Setyawan-Curtarolo variant with explicit branches, segment order,
discontinuities, Cartesian reciprocal lengths, provider version, tolerances,
and time-reversal metadata. It does not calculate electronic or phonon bands.

## Validation and Determinism

Reciprocal, BZ, k-path, and manifest payloads pass their Phase 10I validators
after production provenance and hash binding. Scientific content excludes job
IDs, timestamps, paths, browser state, and future camera state. Repeated direct
and persisted-runtime execution produces byte-identical scientific JSON for
the same normalized input and parameters.

Independent checks compare reciprocal matrices and volumes with NumPy and
retain the reviewed SC/BCC/FCC/hexagonal topology expectations from Phase 10I.
Tetragonal, orthorhombic, monoclinic, and triclinic paths are also exercised,
and conventional/primitive BCC inputs converge to the same standardized
primitive lattice identity.

## Runtime and Security

The Tool Registry entry declares exact input, params, six output types, timeout,
and contract caps. Mock Planner routes explicit English/Chinese BZ data,
reciprocal-lattice, and k-path generation requests. Interactive 3D, electronic
bands, phonons, trajectories, Fermi surfaces, k meshes, charge density, XRD,
CrystalNN, editing, and DFT prompts are excluded.

PlanValidator and QueueWorkerRuntime are unchanged. Persisted runtime evidence
shows one completed tool call and six stored artifacts for valid structures;
singular and non-periodic inputs fail with zero artifacts. Payloads contain no
JavaScript, HTML, CSS, URLs, shader/module code, executable asset, renderer, or
network capability. Error messages are typed and omit paths, stacks, tokens,
environment values, and raw source content. The preview uses fixed component
types and labels; artifact values are rendered as text and cannot supply HTML,
CSS, URLs, modules, shaders, callbacks, or DOM selectors.

## Limits and Deferred Scope

Phase 10I hard caps apply without topology truncation. The registered resource
limits additionally require one structure and at most 512 sites. A cap,
provider, geometry, topology, path, serialization, or manifest failure aborts
the tool rather than emitting a partial scientific claim.

Deferred to Phase 10I-2 or later: Three.js/WebGL BZ rendering, reciprocal-space
picking and inspector UI, labels/axes/camera, point/segment interaction,
band/phonon linkage, browser/GPU/mobile/accessibility evidence, screenshots,
PNG export, custom paths, magnetic/surface/irreducible BZs, meshes, Fermi
surfaces, and electronic/phonon calculation.
