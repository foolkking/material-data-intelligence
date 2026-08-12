# Workspace Report Source Currentness Contract

Workspace currentness is exact identity equality, not latest-resource lookup.
For a current Profile, dataset version authority follows the existing planning
contract: explicit `datasetVersion`, then `sampleIdentity.datasetVersion`, then
the top-level Profile `version` when sample identity is not applicable.

The persisted immutable Workspace source snapshot must equal the Job source
projection for Project, Job, Dataset, dataset version, Profile ID/hash, Intent
ID/hash, Plan ID/hash and Plan schema. A self-consistent but stale snapshot is
still `STALE`; hash tampering, cross-project sources and cross-Job Artifacts are
rejected. This policy performs no scientific recomputation and does not use a
latest, nearest, filename or fuzzy fallback.

