# Current Input Support

This table is derived from current canonical product entries, the sealed Fact/Scope authorities, and production parser/resource paths.

| Input path | Disposition | Boundary |
|---|---|---|
| Tables used by Dataset Intelligence / Materials ML | Supported canonical entry | Supplied tabular facts; bounded Profile semantics |
| CIF / POSCAR structure | Supported canonical entry | Parsed structure facts; no first-principles execution |
| Experimental XRD resource | Supported canonical entry | Explicit wavelength and strict compatibility |
| Trajectory v1 resource | Supported canonical entry | Exact time/cell/identity semantics |
| Typed PhononBand import | `SUPPORTED_WITH_LIMITS` | Explicit declared kind and strict existing schema |
| Typed PhononDos import | `SUPPORTED_WITH_LIMITS` | Explicit declared kind and strict existing schema |
| Generic phonon YAML/JSON | `MAPPING_ONLY` | Not auto-detected or execution-ready |
| Volumetric CHGCAR current canonical path | Supported canonical entry | Persisted bounded field/view contracts |
| Electronic Band / DOS resources | Supported canonical entry | Explicit units/reference/Fermi semantics |

Filename, MIME type, array position, latest resource, or fuzzy matching never establishes scientific identity.
