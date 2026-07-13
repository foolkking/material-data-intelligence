# Phase 10H Phonon Contract

Phase 10H defines an inert, bounded scientific data family for phonon bands, DOS, summaries, and manifests. It does not parse phonon files, calculate force constants, register a tool, render plots, or define eigenvectors.

## Contract family

| Contract | Purpose |
|---|---|
| `phase10h.phonon_band.v1` | One full `3N` branch-major band dataset on an explicit q-point path |
| `phase10h.phonon_dos.v1` | Total and optional projected DOS on a strictly increasing THz grid |
| `phase10h.phonon_summary.v1` | Small JSON-only scientific summary without copied arrays |
| `phase10h.phonon_manifest.v1` | Ordered inert JSON artifact inventory with hashes and sizes |
| `phase10h.qpoint_path.v1` | Shared q-point/path semantics |
| `phase10h.frequency_axis.v1` | Shared frequency and imaginary-mode semantics |
| `phase10h.phonon_source.v1` | Closed provenance and NAC metadata |
| `phase10h.phonon_mode_ref.v1` | Reserved identity name only; no eigenvector payload is defined |

The normative implementation is `mdi_artifact_core.phonon_contract`. Python validates the full scientific contract. TypeScript independently validates the consumer-facing shape, finite numeric values, caps, and inertness.

## Fixed decisions

- Real-space lattice vectors are rows.
- Reciprocal lattice uses the physics `2*pi` convention.
- Canonical q-points are reciprocal fractional coordinates.
- Path distance is global cumulative reciprocal-Cartesian distance in `radian_per_angstrom`.
- Canonical cyclic frequency is `terahertz`.
- Imaginary modes are negative real frequency values.
- Branch identity is source-stable zero-based index; validation never sorts frequencies.
- The first version requires all `3N` branches.
- DOS normalization is `integral(total_dos df) approximately 3N` using the trapezoidal rule.
- Artifacts are closed inert JSON with no URLs, HTML, JavaScript, modules, callbacks, or executable fields.

## Deferred

Phonon parsers, adapters, Tool Registry entries, planner routing, band/DOS/combined plots, eigenvectors, animation, thermal properties, Raman/IR, Brillouin-zone rendering, notebook/script execution, external APIs, and real LLM execution remain separate phases.
