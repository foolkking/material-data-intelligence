# Phase 11 Implementation Backlog

## Phase 11-0

Audit all 62 Registry Tools, Artifacts, Adapters, inputs, evidence, fixtures, references, tolerances, variance risks, and validation gaps. Seal governance and the Phase 11-1 through 11-5 roadmap without changing production science.

## Phase 11-1: Reference Provenance + Safe Fixture Consolidation

Only the following concrete work is approved for future reviewer admission:

| Capability | Source needed | Fixture/evidence | License and transformation |
|---|---|---|---|
| CrystalNN/VoronoiNN | exact official library version/docs and retained source cases | immutable source cases with source checksum; self-reference labeled | record upstream license; bounded normalization only |
| Phonon band/DOS/combined | retained official project examples already mapped | source-hash-bound normalized band/DOS cases | establish redistribution/derived-data status and transformation log |
| Electronic Band/DOS | provenance for controlled supplied-output fixtures | immutable gapped, gapless, spin, projection-completeness fixtures | source/license disposition; no calculation execution |
| Volumetric | retained CUBE/VASP sample provenance | bounded scalar-field fixtures and source checksums | license review; preserve numeric values |
| Historical official examples | retained Phase 10F and related inventories | deduplicated source-reference registry | classify direct, mapping-only, extraction-required, superseded |

No numeric PASS is declared in 11-1. No notebook, downloaded script, or external scientific API is executed.

## Phase 11-2: Golden Scientific Benchmark Suite

| Tool/version | Fixture | Expected values/invariants | Unit/tolerance | Cases | Dependency |
|---|---|---|---|---|---|
| `structure.local_environment_polyhedra@0.1.0` | exact regular/distorted bounded polyhedra | geometry distances, hull/face invariants, identity preservation | contract-owned per quantity | positive, tie, degenerate, invalid | independent reference provenance from 11-1 where used |
| `structure.experimental_xrd_comparison@0.1.0` | analytic peak lists plus bounded sampled signal | detected identities, one-to-one pairs, signed residuals, unmatched sets | degree 2theta; N3 policy | match, tie, zero-match, wavelength mismatch | none |
| `trajectory.rdf@0.1.0` | periodic lattice and uniform/synthetic distributions | exact bin edges, pair counts, normalized g(r), window/species coverage | angstrom/dimensionless; N4 policy | whole, window, species, radius invalid | none |
| `trajectory.msd/diffusion@0.1.0` | stationary, constant velocity, random walk | unwrapped displacement, MSD, D relation, ballistic rejection | ps, angstrom squared, angstrom squared/ps | positive and scientific non-qualification | none |
| `structure.brillouin_zone@0.1.0` | analytic reciprocal cells | volume and topology invariants | contract symmetry/geometry tolerance | cubic, triclinic, invalid | none |
| ML/composition quantitative Tools | controlled tables with analytic metrics | exact counts, metrics, seed/sign invariants | metric-owned | positive, missing/invalid, tie | none |
| electronic Tools | immutable supplied resources | gap/VBM/CBM/path, DOS channels/completeness | eV/source DOS semantics | direct/indirect/gapless/spin/partial | `BLOCKED_BY_11_1_REFERENCE_EXTRACTION` for official-derived claims |

Existing evidence is reused when hashes, contracts, units, tolerances, and locked authority dependencies match.

## Phase 11-1 Completion Handoff

The Phase 11-1 evidence pack is generated under `evidence/phase11_1_reference_provenance_safe_fixture/`. It reconciles all 12 Phase 11-0 gaps, retains the observed repository counts (46 reference-like, 170 retained fixtures, 55 official/example records), preserves the Phase 11-0 tolerance registry, and supplies a typed 11-2 benchmark input manifest. No numeric validation or validation-level promotion occurs here.

## Phase 11-3: Reproducibility Matrix

- OS: locked Linux CI and locked Windows primary runtime.
- Python/scientific libraries: repository lockfile exact versions only.
- macOS: `NOT_RELEASE_TARGET` unless separately established.
- browsers: Chromium, Firefox, WebKit, Chromium 390x844.
- outputs: `EXACT`, `TOLERANCE_BOUNDED`, `DISPLAY_ONLY_VARIANCE`, `UNSUPPORTED_PLATFORM`, or `KNOWN_LIMITATION`.

## Phase 11-4: Honest Coverage

Publish Tool, Input, and Official/Candidate Example matrices under the exact verdict criteria in `phase11_validation_governance.md`. Mapping, fixture existence, screenshots, and browser rendering cannot promote numeric scientific status.

## Phase 11-5: Closure

Require a Reference Registry, Golden Benchmark Suite, Tolerance Registry, Variance Matrix, Tool Validation Matrix, Input Support Matrix, Honest Example Coverage Matrix, Reproducibility Report, Known Scientific Limitations, Evidence Manifest, and final acceptance. Target wording is `COMPLETE / REFERENCE_VALIDATED_WITH_EXPLICIT_LIMITS`, never `ALL_SCIENCE_CORRECT`.
