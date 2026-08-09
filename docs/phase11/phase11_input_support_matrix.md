# Phase 11 Input Support Matrix

The exact matrix is [input_support_matrix.json](evidence/phase11_0_validation_baseline_reconciliation/input_support_matrix.json). Verdicts require an actual platform path through upload/sniffing, parser, resource contract, DataProfile, Eligibility/Planner, Runtime, and Workspace where applicable.

Current audited headline verdicts:

| Input family | Verdict | Boundary |
|---|---|---|
| CSV | DIRECT_SUPPORTED | bounded table path |
| canonical typed JSON | SUPPORTED_WITH_LIMITS | strict schema and duplicate-key rejection |
| CIF | DIRECT_SUPPORTED | pymatgen Structure path |
| POSCAR/CONTCAR | DIRECT_SUPPORTED | canonical name/content recognition |
| XYZ | SUPPORTED_WITH_LIMITS | single-frame structure semantics |
| EXTXYZ | SUPPORTED_WITH_LIMITS | stable identities and explicit physical time required by MSD/diffusion |
| VASP volumetric files | SUPPORTED_WITH_LIMITS | recognized canonical names and voxel caps |
| Gaussian CUBE | SUPPORTED_WITH_LIMITS | single dataset only |
| ZIP | SUPPORTED_WITH_LIMITS | safe bounded member dispatch |
| supplied electronic Band/DOS JSON | SUPPORTED_WITH_LIMITS | canonical resource only, no DFT |
| phonon YAML/JSON | MAPPING_ONLY | no claimed generic upload parser |
| XLSX/Excel | UNSUPPORTED | no platform parser path |
| Parquet | UNSUPPORTED | no platform parser path |
| LAMMPS trajectory | UNSUPPORTED | no platform parser path |

Library theoretical capability is not platform support. Unsupported inputs cannot be promoted by documentation or example mapping.
