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

The checked-in interpretability inventory audits all currently available tools
at artifact-contract granularity. A tool-level aggregate state is only a
summary: every declared artifact independently records whether it is projector
ready, display-only, unsupported, untrusted text, or provenance without
scientific facts. One unsafe or display artifact does not reclassify another
stable structured contract as interpretation-ready or unsafe.

The interpretation service owns one read-only projector contract registry keyed
by exact `(toolId, artifactType)`. Every interpretation-ready pair declares its
contract family, accepted contract versions, media-type allowlist, and projector
version. Runtime projection and the retained inventory consume that same
registry; unversioned Registry artifact declarations remain explicitly
`UNVERSIONED_REGISTRY_ARTIFACT_TYPE` and cannot become evidence authority.
