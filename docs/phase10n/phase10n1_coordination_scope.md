# Phase 10N-1 CrystalNN / VoronoiNN Coordination Scope

Status: `AUTHORIZED / N1-R0 CONTRACT SEALED FOR IMPLEMENTATION`.

This document is the exact N1 product and contract authority. The corrective reviewer
authorization supersedes the earlier proposal gaps. Implementation may add only the two
tools and contracts listed here.

## Registry and algorithm authority

| Product | Exact Tool | Tool version | Adapter | Algorithm ID | Locked API |
| --- | --- | --- | --- | --- | --- |
| CrystalNN coordination | `structure.coordination_crystalnn` | `0.1.0` | `CrystalNNCoordinationAdapter` | `pymatgen.crystalnn` / `2026.5.4` | `pymatgen.core.local_env.CrystalNN.get_nn_info(structure, n)` |
| VoronoiNN coordination | `structure.coordination_voronoinn` | `0.1.0` | `VoronoiNNCoordinationAdapter` | `pymatgen.voronoinn` / `2026.5.4` | `pymatgen.core.local_env.VoronoiNN.get_nn_info(structure, n)` |

The installed authority is `pymatgen 2026.5.4`, `pymatgen-core 2026.5.18`, MIT license.
The Registry advances from 53 to exactly 55 tools. There is no comparison Tool or
comparison Adapter. Comparison is a deterministic presentation over one exact Artifact
from each algorithm bound to the same immutable structure hash.

Canonical references are `structure.coordination_crystalnn@0.1.0` and
`structure.coordination_voronoinn@0.1.0`.

## Exact parameter contracts

Both schemas reject additional properties, non-finite numbers and coercion. Defaults are
resolved before execution, canonically serialized as sorted JSON, hashed with SHA-256 and
persisted in the Artifact.

### CrystalNN parameters

| Name | Type | Default | Bound / value | Meaning |
| --- | --- | --- | --- | --- |
| `weighted_cn` | boolean | `true` | boolean | Preserve CrystalNN weights and weighted-CN semantics. |
| `distance_cutoff_low` | number | `0.5` | `0..5`, finite | Lower relative distance cutoff in angstrom. |
| `distance_cutoff_high` | number | `1.0` | `0..5`, finite, not below low | Upper relative distance cutoff in angstrom. |
| `x_diff_weight` | number | `3.0` | `0..10`, finite | Electronegativity-difference weighting. |
| `porous_adjustment` | boolean | `true` | boolean | Locked CrystalNN porous adjustment. |
| `search_cutoff_angstrom` | number | `7.0` | `1..20`, finite | Neighbor search cutoff in angstrom. |
| `max_structures` | integer | `32` | `1..32` | Structures retained per request. |
| `max_sites` | integer | `5000` | `1..5000` | Sites evaluated per structure. |
| `max_neighbors_per_site` | integer | `1000` | `1..1000` | Candidate/result cap per site. |
| `max_retained_rows` | integer | `50000` | `1..50000` | Total retained neighbor rows. |

`cation_anion=false` and `fingerprint_length=null` are fixed implementation values and
are recorded under `fixedParameters`; they are not user parameters. N1 does not infer or
assign oxidation states. A disordered or partial-occupancy site is rejected with typed
unsupported input rather than coerced.

### VoronoiNN parameters

| Name | Type | Default | Bound / value | Meaning |
| --- | --- | --- | --- | --- |
| `tol` | number | `0.0` | `0..1`, finite | Relative solid-angle tolerance. |
| `cutoff_angstrom` | number | `13.0` | `1..20`, finite | Voronoi neighbor search cutoff. |
| `allow_pathological` | boolean | `false` | boolean | Whether pathological cells may return bounded results. |
| `max_structures` | integer | `32` | `1..32` | Structures retained per request. |
| `max_sites` | integer | `5000` | `1..5000` | Sites evaluated per structure. |
| `max_neighbors_per_site` | integer | `1000` | `1..1000` | Candidate/result cap per site. |
| `max_retained_rows` | integer | `50000` | `1..50000` | Total retained neighbor rows. |

`weight=solid_angle`, `extra_nn_info=true`, and `compute_adj_neighbors=true` are fixed and
recorded. N1 stores normalized solid-angle weights. Unknown upstream kwargs are rejected.

## DataProfile 2.1

`profileContractVersion` accepts `2.0` and `2.1`. A 2.1 Profile adds optional
`coordinationReadiness`, with this exact shape:

```json
{
  "contractVersion": "1.0",
  "periodicStructurePresent": true,
  "eligibleStructureCount": 1,
  "structures": [{
    "objectId": "object-id",
    "objectHash": "64-lowercase-hex",
    "periodic": true,
    "latticeStatus": "VALID",
    "siteCount": 2,
    "speciesOccupancyStatus": "ORDERED_FULL_OCCUPANCY",
    "disorderStatus": "ORDERED",
    "partialOccupancyStatus": "ABSENT",
    "coordinationInputStatus": "READY",
    "reasons": []
  }],
  "status": "READY",
  "reasons": []
}
```

Allowed status values are `READY`, `MISSING_REQUIRED_DATA`, `AMBIGUOUS`, and
`UNSUPPORTED_DATA_KIND`. Lattice status is `VALID`, `MISSING`, or `INVALID`;
species/occupancy status is `ORDERED_FULL_OCCUPANCY`, `DISORDERED`,
`PARTIAL_OCCUPANCY`, or `UNSUPPORTED`. Profile generation is deterministic and does not
run either coordination algorithm. DataProfile 2.0 remains readable; there is no bulk
backfill, database migration or new API family.

## Artifact contracts

The primary persisted file remains inert `table_json`; its embedded discriminator is
strict and algorithm-specific:

- CrystalNN: `artifactType=structure.coordination_crystalnn`,
  `schema_version=phase10n1.crystalnn_coordination.v1`.
- VoronoiNN: `artifactType=structure.coordination_voronoinn`,
  `schema_version=phase10n1.voronoinn_coordination.v1`.

Each payload contains `tool`, `algorithm`, `library`, `resolvedParameters`,
`fixedParameters`, `parameterHash`, `scope`, `structures`, `siteResults`, `coverage`,
`warnings`, `unsupportedSites`, `runtimeDiagnostics`, `provenance`, `limits`, and
`security`. Full source structures are not copied.

`scope` binds project, dataset, Job, Plan/version when available, ToolCall, input resource
ref/hash and structure hash. `siteResults` bind structure hash, center site identity,
algorithm-specific coordination semantics/value, and ordered neighbor relations.

## Identity and ordering

- Structure identity: `sha256` of canonical immutable structure input.
- Site identity: `site:<structure-sha256>:<zero-based-index>`. The index is valid only
  inside that exact structure hash and is never cross-version identity.
- Neighbor identity:
  `neighbor:<algorithm-id>:<parameter-hash>:<structure-hash>:<center-index>:<neighbor-index>:<i>,<j>,<k>`.
- Periodic image: exact bounded integer triplet `[i,j,k]` from locked pymatgen output.
- Canonical neighbor order: center site index, neighbor site index, periodic image,
  distance, weight. Site order is structure hash then site index.

Species/occupancy and fractional coordinates are retained in site refs for validation,
but labels, coordinates or species alone are never rebinding authority. Identity and
periodic images use exact equality.

## Semantics and units

Distance is angstrom; periodic image and coordination values are dimensionless.
CrystalNN reports `weighted_coordination_number=sum(returned weights)` and
`neighbor_count`; VoronoiNN reports `weighted_coordination_number=sum(solid-angle
weights)` and `neighbor_count`. These algorithm-specific quantities are never relabeled
as a common absolute coordination truth. Raw algorithm weights are retained. Floating
values use deterministic 12-decimal serialization without changing identity decisions.

## Coverage, errors and caps

Coverage records total, eligible, successful, unsupported and failed sites, zero-neighbor
sites, retained rows and a ratio. Partial per-site output is allowed; failures remain
typed and comparison reports incomplete inputs.

Canonical N1 error details use existing `TOOL_INPUT_INVALID`, `TOOL_PARAM_INVALID`,
`TOOL_RESOURCE_LIMIT`, `TOOL_EXECUTION_FAILED`, or `TOOL_OUTPUT_INVALID` envelopes with
these `errorType` values: `UNSUPPORTED_NON_PERIODIC_STRUCTURE`, `MISSING_LATTICE`,
`INVALID_LATTICE`, `EMPTY_STRUCTURE`, `NON_FINITE_STRUCTURE_VALUE`,
`UNSUPPORTED_DISORDER`, `UNSUPPORTED_PARTIAL_OCCUPANCY`, `SITE_IDENTITY_INVALID`,
`SITE_INDEX_OUT_OF_RANGE`, `STRUCTURE_IDENTITY_MISMATCH`, `STALE_SOURCE`,
`SOURCE_CHECKSUM_MISMATCH`, `STRUCTURE_TOO_LARGE`,
`NEIGHBOR_CANDIDATE_LIMIT_EXCEEDED`, `ALGORITHM_PARAMETER_INVALID`, `ALGORITHM_FAILED`,
`PATHOLOGICAL_VORONOI_CELL`, `NO_COORDINATION_RESULT`, `ARTIFACT_TOO_LARGE`,
`FOREIGN_PROJECT_SOURCE`, and `FOREIGN_JOB_SOURCE`.

Hard caps are 32 structures/request, 5,000 sites/structure, 1,000 neighbors/site, 50,000
retained rows, 16 MiB primary JSON and 120 seconds. The implementation validates caps
before retaining rows and never performs unbounded frontend neighbor work.

## Fixtures and tolerances

Checked inert fixtures include ordered diamond Si, rocksalt NaCl, a periodic-image case,
an algorithm-disagreement case, partial occupancy rejection, pathological Voronoi input,
and small/medium/near-cap controls. Exact locked-version output is
`OFFICIAL_DERIVED_VERIFIED`; analytic identity/cap cases are `SYNTHETIC_CONTROLLED`.

- structure/site/periodic-image identity and ordering: exact;
- distance: absolute `1e-6 angstrom`;
- neighbor weight: absolute `1e-8`, relative `1e-6`;
- coordination value: absolute `1e-8`, relative `1e-6`;
- canonical checksum and parameter hash: exact.

## Product integration and wording

Eligibility uses Profile 2.1 readiness without executing algorithms. Planner and
PlanValidator select exact tools/versions and existing Plan 0.1/0.2 bindings. Runtime
resolves the registered Adapter, validates source identity, and persists through existing
PostgreSQL/Redis/MinIO authorities.

Workspace uses an adapted coordination table plus persisted-Artifact Structure Viewer
overlay. Selection uses exact Artifact, structure-bound `PERIODIC_SITE`, and
algorithm-specific neighbor identity encoded in bounded selection metadata. Inspector,
interpretation, Report and Recipe retain algorithm/version, parameters, source hashes,
coverage, warnings and provenance. Comparison consumes two exact same-structure Artifacts
and never recomputes or selects a preferred algorithm.

Allowed wording is `algorithm-derived coordination`, `CrystalNN-derived coordination`,
`VoronoiNN-derived coordination`, and `neighbor relation identified by the selected
algorithm`. Definitive bonding, absolute coordination truth, experimental confirmation,
oxidation-state inference, algorithm fallback and result substitution are prohibited.

## Compatibility and non-scope

`structure.coordination_hist` remains an independent distance-cutoff legacy capability;
it is not relabeled or rebound. Existing 53 tools, historical Profiles, Plans, Artifacts,
Workspaces, selection URLs, Reports and Recipes remain readable. N2 local-environment
classification/polyhedra and all later Phase 10N science remain outside N1.

Database schema, migration head `0007_phase10m1_workspace_domain`, public API families,
dependencies, lockfile, Workspace authority, Selection authority, Report/Recipe execution
boundary and DeepSeek-only policy remain unchanged.
