# Phase 10L-4 Evidence Projectors

`phase10l4.projectors.v1` validates each supported Artifact contract before
extracting bounded structured facts. Supported production families are:

| Family | Artifact types |
| --- | --- |
| Dataset/property | `table_json` |
| Materials ML | `metrics_json` |
| Structure | `structure_json` |
| Phonon | `phonon_band_json`, `phonon_dos_json`, `phonon_band_dos_json`, `phonon_summary_json` |
| Volumetric | `volumetric_field_json` |

Projectors preserve identity, units, references, warnings, and checksums. They
perform no new scientific algorithm, LLM call, network access, raw text
interpretation, filename inference, or unit/target guessing. Unsupported
contracts remain explicit limitations and do not yield scientific claims.
