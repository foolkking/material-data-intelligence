# Artifact Availability Audit — 2026-09-01

## Scope and safety

This is a read-only audit of the retained same-stack qualification environment at repository
HEAD `9864e79c433536cc90b24c6a4c68c5bebd940daa`.

The audit inspected:

- PostgreSQL scientific object/version payload references;
- `source_resource_refs_json` relationship integrity;
- Dataset raw, normalized and metadata object keys;
- persisted Artifact storage keys and providers;
- the objects currently present in the active MinIO endpoint and its buckets;
- existing recovery evidence and the tests which created the unresolved records.

No application code, PostgreSQL row, MinIO object, service process or browser process was
changed by this audit.

## Executive verdict

The unavailable-payload screens are **not caused by a stopped core service** and are **not
caused by the browser-facing API selecting SQLite or local artifact storage**.

At audit time:

| Runtime component | Observed state |
| --- | --- |
| API | healthy on `127.0.0.1:8005` |
| PostgreSQL | reachable on `127.0.0.1:55434`, database `mdi` |
| Redis | reachable on `127.0.0.1:6379` |
| MinIO | reachable on `127.0.0.1:9000`, active bucket `mdi-artifacts` |
| frontend | listening on `127.0.0.1:3013` |
| workers | six Redis-backed workers present |
| `/health/runtime` | `database=postgresql`, `redis=redis`, `artifactStorage=minio`, `worker=redis` |

The current discrepancy is data-specific:

1. **One acceptance-principal Dataset has three absent MinIO objects.** Its raw and normalized
   payloads are cryptographically recoverable from the authoritative test input and current
   parser/exporter contract.
2. **Forty-four ScientificObjectVersion rows are service-test residue.** The creating tests
   persisted placeholder payload references but never wrote corresponding MinIO objects.
3. **Two Artifact rows explicitly use `storage_provider=local`.** They are old Phase 6 test
   fixtures and are not missing MinIO artifacts.

The active user's legitimate ScientificObjectVersion payloads are otherwise present. There
is no evidence of a current global MinIO outage or current runtime configuration drift.

## Inventory and reconciliation

### PostgreSQL authority counts

| Authority | Rows |
| --- | ---: |
| `artifacts` | 1,565 |
| `datasets` | 181 |
| `scientific_objects` | 213 |
| `scientific_object_versions` | 249 |
| unique referenced storage keys collected | 1,849 |

The 1,849 unique keys were collected from:

- `artifacts.storage_key`;
- `scientific_object_versions.normalized_payload_ref_json.object_key`;
- `datasets.metadata_json.rawUploads[].storageKey`;
- `datasets.metadata_json.normalizedExports[].storageKey`;
- `datasets.metadata_json.normalizedExports[].metadataKey`.

Authority-row contribution before key de-duplication:

| Reference family | Rows |
| --- | ---: |
| Artifact keys | 1,565 |
| ScientificObjectVersion normalized payload keys | 249 |
| Dataset raw keys | 25 |
| Dataset normalized keys | 25 |
| Dataset normalized metadata keys | 25 |

### Current active MinIO

The active endpoint contains three retained buckets:

| Bucket | Objects |
| --- | ---: |
| `mdi-artifacts` | 1,844 |
| `mdi-phase14r-sb-20260901-1930` | 219 |
| `mdi-phase14r-sb-20260901-2010` | 219 |

Current key and expected-size reconciliation:

| Result | Unique refs |
| --- | ---: |
| present at exact key with expected size | 1,800 |
| not present at exact key in active MinIO | 49 |
| present but expected-size mismatch | 0 |

The 49 keys absent from active MinIO classify as:

| Class | Count | Product impact |
| --- | ---: | --- |
| acceptance Dataset raw/normalized/metadata | 3 | user-visible and recoverable |
| service-test ScientificObjectVersion placeholders | 44 | generated test projects; not legitimate payload loss |
| explicit local-provider Phase 6 Artifacts | 2 | not MinIO references |

Correctly excluding the two `storage_provider=local` rows, there are **47 absent
MinIO-backed references**: three recoverable Dataset objects plus 44 test-fixture placeholder
references.

### Source-resource integrity

All 249 ScientificObjectVersion rows have a non-empty `source_resource_refs_json` list:

| Source-resource class | Count |
| --- | ---: |
| Dataset/project reference | 230 |
| explicit `system_fixture` reference | 19 |
| broken referenced Dataset/project relationship | 0 |

The failure is therefore not a broken PostgreSQL source relationship. It is the difference
between a valid relational reference and whether the referenced payload bytes were ever
written to durable object storage.

## Classification

### A. Service not started

**Count: 0**

PostgreSQL, Redis, MinIO, API, frontend and Redis-backed workers were all reachable. The
runtime health endpoint reported the same real service topology. Restarting services will
not recreate absent object bytes.

### B. Current configuration mismatch

**Count: 0**

The browser-facing API uses PostgreSQL and the active MinIO endpoint/bucket. There is no
current evidence of the earlier SQLite/local-storage runtime mismatch.

### C. Recoverable acceptance Dataset

**Affected Dataset count: 1**
**Affected object-key count: 3**

| Field | Exact identity |
| --- | --- |
| user | `user_local` / `acceptance.researcher@local.invalid` |
| project | `project_0001_d286007db78e427e` |
| project name | `Input transport regression` |
| Dataset | `dataset_0001_a0b09e3324e44ca4` |
| normalized object | `obj_dataframe_60c91184df02` |
| Dataset status | `profile_ready` |
| normalized object hash | `60c91184df022d34cb4f8c5f7ae9444dc3abbd41f069e694329edc75b93d357c` |

Missing exact keys:

1. `projects/project_0001_d286007db78e427e/datasets/dataset_0001_a0b09e3324e44ca4/raw/file_001_7309387f/materials.zip`
2. `projects/project_0001_d286007db78e427e/datasets/dataset_0001_a0b09e3324e44ca4/normalized/obj_dataframe_60c91184df02/data.json`
3. `projects/project_0001_d286007db78e427e/datasets/dataset_0001_a0b09e3324e44ca4/normalized/obj_dataframe_60c91184df02/metadata.json`

Expected raw payload:

| Property | Value |
| --- | --- |
| format | ZIP_STORED archive containing `materials.csv` |
| member bytes | `formula,value\nSi,1\n` |
| byte size | 143 |
| SHA-256 | `b75f9a1d398de4636e4494f2aaa04977326ca66a96356fcc1be87e86a3a520c4` |

The exact raw ZIP was reconstructed in memory using the persisted creation time and the
test's deterministic archive input. The result is exactly 143 bytes and its SHA-256 equals
the database authority above.

Expected normalized payload:

```json
[
  {
    "formula": "Si",
    "value": 1
  }
]
```

| Property | Value |
| --- | --- |
| byte size | 47 |
| SHA-256 | `d9067205ffb2aba89112d17662fef3eeaca2dabc0ba02a2a4a00063a24561daf` |

Running the current parser in a temporary directory against the reconstructed raw ZIP
produced:

- parse status `success`;
- object ID `obj_dataframe_60c91184df02`;
- object type `DataFrame`;
- normalized object hash
  `60c91184df022d34cb4f8c5f7ae9444dc3abbd41f069e694329edc75b93d357c`;
- one row, columns `formula` and `value`;
- the exact 47-byte normalized payload and expected SHA-256.

No byte-identical raw or normalized duplicate exists under another key in any bucket on the
active MinIO endpoint. This is therefore **not a simple active-bucket path rename**. It is a
durability leak from
`tests/test_phase_d_r2_1_input_transport.py::test_binary_zip_bytes_survive_browser_api_materialization`:
the test persisted its Dataset in shared PostgreSQL while writing bytes into its temporary
local Artifact root.

The Dataset has no ScientificObject, ScientificResult or Report dependency. Its relational
authority is limited to the Dataset and DataProfile records.

The metadata object has no independent expected checksum stored in PostgreSQL. It can be
reconstructed canonically from the exact parsed object, the existing storage key/content
hash, parser metadata and provenance. That reconstruction is semantically safe, but it must
be recorded as a reconstructed metadata wrapper rather than claimed to be byte-identical to
the lost historical wrapper.

### D. Service-test ScientificObjectVersion residue

**Version count: 44**
**ScientificObject count: 35**
**Project count: 35**
**Object type: `structure.crystal` for all 44**
**Current recorded availability: `AVAILABLE` for all 44**

These rows were created by service-backed integration tests with generated owners and
projects. Their test implementations persist placeholder keys/checksums and do not write the
referenced payload into MinIO:

- Phase 1 concurrency fixtures: 12 versions under `agent2/<suffix>/<0..3>.json`;
- Phase 2 fixtures: 7 versions under `agent2-phase2/<suffix>.json`;
- Phase 3 fixtures: 25 versions under `agent2-phase3/<suffix>.json`.

They are not authorized to the acceptance researcher. No ScientificResult snapshot,
Report or Report snapshot references any of the 44 versions. Thirty-two test
ResearchContextSnapshot rows reference a subset of them, so blind row deletion is not safe.

#### Phase 1 — 12 versions / 3 projects

Projects:

- `agent2-project-42d8df32872d`
- `agent2-project-62f534ba64da`
- `agent2-project-e16ab81b4210`

Version IDs:

- `97383913-9245-4b71-bf86-a9d23361b27e`
- `155179fc-581f-4d25-9ca6-45b41f80b57d`
- `4e1a5031-71a2-48b3-ab79-cc7645258f76`
- `13c65c1a-2eac-4661-8c71-923a1ba0bb5f`
- `0637ee85-cba9-43f5-ab74-ffd61c5b2bae`
- `c4d484af-2c4d-4cf1-a35f-d9c89594c641`
- `b803586e-670a-4330-a8aa-3081e26fc22c`
- `9fb60259-a2d2-4c98-81fd-aeb019637aab`
- `11d52eb2-48e5-448b-a277-619df1e48711`
- `a9952811-83fe-4834-8187-0b9c0f9bb911`
- `3f3e2421-cc16-4edc-b06a-a9d3dc5fd0be`
- `08567f7a-0bcb-4641-8a79-93fcf1efce1e`

#### Phase 2 — 7 versions / 7 projects

Version IDs:

- `28e3c65e-b1f9-40a2-a6f4-9188c1ea9fbf`
- `4f85122b-febc-4fcc-9f3a-a3e733b1f7b0`
- `89392ba5-d920-4081-ada3-b8244095d2e6`
- `0f13698e-c618-41be-b979-fab8fc56404d`
- `17eefa8f-492d-4481-a761-1ef2f0e0f45b`
- `3187f0a4-b875-4ce3-9df2-3acb9c589b10`
- `a62197d8-9ce4-4bb4-98c0-281be2bcd9cf`

#### Phase 3 — 25 versions / 25 projects

Version IDs:

- `884f4921-22d9-45ed-a072-d138c7414b8c`
- `af696793-78b4-410a-87f8-c7111e891e48`
- `1c2a8ec4-b845-48ff-bc87-4d17d8ee996c`
- `bd5e7986-1ecd-4d8b-a59c-c887e08eabff`
- `85090ee9-d386-4055-a0d3-476c661f93f5`
- `a952a5c3-4543-42de-a7c2-8c9555a7a672`
- `efa04f75-47a9-4cf4-a747-b3d05d0e5384`
- `9d0541da-e05c-4fba-bf67-2cc08c769cfe`
- `223e7098-d476-47b2-8bec-26ea999c54cd`
- `846aa38d-e948-4217-b17b-1cead0d3fbea`
- `395af032-92ff-497f-97c2-aafefc12cde5`
- `82c566bd-ff70-4150-a4f7-03b637199016`
- `58de24bb-8339-4a2f-9ec7-8d419ad98c5d`
- `b0f38b40-529c-467a-a830-937149ab84cf`
- `c98f819a-1364-4984-96fb-bf2b9f974dd4`
- `558d715f-db70-4a28-9643-01aa55e8646a`
- `0fb8c7d1-fc03-4df7-808d-95b286e8da39`
- `e34ac856-0ad5-4881-b40f-37a6a99abe36`
- `f851fd06-9a34-430d-930a-d6d861721f9a`
- `60b9d63b-b37a-4425-a96e-c17254ac450c`
- `e34614d9-195a-47b7-86ac-0cb41c6bfc6c`
- `6f52cf61-8a7a-4ea2-9a87-705c54e9ba50`
- `8362bea8-d7d7-47e4-bfe0-15cf47a82af4`
- `2aa532a9-38ad-4ca3-b810-a9484d64a344`
- `e387e533-a797-4980-9740-6be816ecef4d`

These cannot be legitimately “recovered” by inventing JSON which satisfies the placeholder
references. The safe correction is to isolate service-test storage/database state and
quarantine or accurately mark existing fixture versions, not to fabricate scientific bytes.

### E. Explicit local-provider Artifact fixtures

**Artifact count: 2**

| Artifact ID | Project | Storage provider | Storage key |
| --- | --- | --- | --- |
| `art_live_1` | `proj_p6_1` | `local` | `live/metrics.json` |
| `art_loop` | `proj_p6_9` | `local` | `projects/proj_p6_9/jobs/job_p6_9/tool_calls/call_job_p6_9_step_metrics/art_loop.json` |

Both are Phase 6 test records created by `test_user`. They should be excluded from a MinIO
availability denominator because PostgreSQL explicitly records another provider. They have no
acceptance-user impact.

## Acceptance-principal scope

The acceptance account maps to `user_local`. It owns 16 projects; 13 of those projects
currently contain storage-backed authorities.

Across the acceptance-owned storage-backed scope:

| Metric | Count |
| --- | ---: |
| unique referenced keys | 75 |
| present | 72 |
| missing | 3 |

All three missing keys belong to
`dataset_0001_a0b09e3324e44ca4`. No acceptance-owned ScientificObjectVersion normalized
payload is missing.

The supplied screenshot labels the unavailable surface as a trajectory. That label does not
match any currently missing acceptance-owned ScientificObjectVersion payload, and all 44
payload-less generated versions are `structure.crystal`, not trajectory objects. If the
trajectory screen remains reproducible after the Dataset recovery, capture its exact browser
route, project ID, object ID and version ID. It would then indicate a different defect such
as stale browser/runtime state, incorrect route identity, or unintended discovery of a test
project; it is not explained by the current authoritative storage-key reconciliation.

Expected result after the Dataset recovery batch:

```text
acceptance-owned referenced keys = 75
present = 75
missing = 0
```

## Historical path drift

Existing evidence in
`docs/agent2/phase14r/PAYLOAD_AVAILABILITY_REMEDIATION_RESULTS.md` records an earlier retained
MinIO-root split. That campaign recovered 1,551 referenced objects and reduced the then-known
unresolved set to five.

The current audit refines the remaining classification:

- two of the five are explicitly local-provider Phase 6 fixtures;
- the remaining three belong to one Dataset and are now proven recoverable;
- the additional 44 missing version keys were produced later by tests which never wrote
  payload bytes.

This report supersedes only the earlier conclusion that the Dataset raw/normalized bytes
were unrecoverable. It does not rewrite or invalidate the historical recovery evidence.

## Safe batch remediation plan

No remediation was executed during this audit.

### Batch 1 — restore the one acceptance Dataset

This batch is safe to automate because the raw and normalized payloads have exact expected
hashes and reproduce the persisted object identity.

1. Generate the 143-byte ZIP from the authoritative test input and timestamp.
2. Assert SHA-256 equals
   `b75f9a1d398de4636e4494f2aaa04977326ca66a96356fcc1be87e86a3a520c4`.
3. Parse it with the current parser in memory.
4. Assert object ID, object hash, schema, row count, column identities and normalized
   SHA-256 exactly match PostgreSQL.
5. Use conditional create semantics to write the raw and normalized bytes only to their
   already-authoritative exact keys. Do not overwrite a concurrently restored object.
6. Reconstruct the metadata wrapper through the current normalized-object exporter contract,
   preserving exact object/key/content-hash/provenance fields and recording recovery
   provenance.
7. Read all three objects back, re-run checksum/parser validation and verify Data Platform,
   Table and Viewer routes.
8. Make no ScientificObjectVersion, Result or Report identity change.

Expected delta:

```text
active MinIO object keys +3
acceptance missing refs 3 -> 0
ScientificObjectVersion rows delta = 0
ScientificResult rows delta = 0
Report rows delta = 0
```

### Batch 2 — stop test fixtures leaking into shared durable authority

Change the three integration-test fixture families so they use isolated PostgreSQL
schema/database and isolated MinIO bucket/prefix with deterministic teardown. A test which
asserts `availability_status=AVAILABLE` must write a real payload with a real checksum.

For the existing 35 generated projects:

1. select only the exact generated-project prefixes listed above;
2. re-run the dependency scan;
3. assert no acceptance-user membership, ScientificResult or Report dependency;
4. preserve/audit the 32 test ContextSnapshots;
5. use a domain maintenance command to quarantine the generated projects and mark the 44
   payload-less versions `SOURCE_MISSING`, or remove the whole isolated test graph only if
   every foreign-key dependency is included;
6. never invent payload bytes for placeholder checksums.

Expected product effect: these records cease claiming `AVAILABLE` when no bytes exist, while
legitimate historical scientific authority remains untouched.

### Batch 3 — provider-aware availability reporting

Availability audits and health dashboards should compare an Artifact only with the backend
named by `storage_provider`. The two local Phase 6 fixtures must not appear as MinIO loss.
They may later be removed with their complete test graph after explicit maintenance approval.

### Batch 4 — recurring integrity guard

Add a read-only scheduled integrity check which reports:

- key existence by declared provider;
- expected byte size and checksum when authority supplies them;
- `AVAILABLE` versions whose payload is absent;
- broken source-resource relationships;
- unauthorized/test-project leakage into normal discovery;
- orphan storage objects separately from referenced missing objects.

The guard must report and fail qualification; it must not silently delete or synthesize data.

## Recommended repair order

1. Restore the three exact Dataset keys.
2. Browser-verify the acceptance Dataset and all normal Viewer/Table routes.
3. Isolate future service tests.
4. Quarantine or accurately mark the 44 existing placeholder versions.
5. Make availability metrics provider-aware.
6. Run the recurring integrity guard and confirm:

```text
acceptance-owned missing refs = 0
AVAILABLE scientific versions with absent durable payload = 0
broken source-resource relationships = 0
```

## Final classification

```text
SERVICE_NOT_RUNNING = NO
CURRENT_RUNTIME_CONFIGURATION_ERROR = NO
ACTIVE_MINIO_PATH_ALIAS_RECOVERY = 0

USER_VISIBLE_RECOVERABLE_DATASETS = 1
USER_VISIBLE_RECOVERABLE_KEYS = 3

SERVICE_TEST_PLACEHOLDER_VERSIONS = 44
SERVICE_TEST_GENERATED_PROJECTS = 35

EXPLICIT_LOCAL_PROVIDER_TEST_ARTIFACTS = 2

BROKEN_SOURCE_RESOURCE_RELATIONSHIPS = 0
PRESENT_REFERENCES_WITH_SIZE_MISMATCH = 0
```

The professional product fix is therefore a bounded recovery plus fixture isolation, not a
service restart and not a Viewer workaround.

## Executed acceptance-scope remediation

The bounded Dataset recovery described above was executed after an independent preflight.
The raw ZIP was reconstructed with the persisted local ZIP timestamp and the authoritative
test input, then rejected unless its 143 bytes matched SHA-256
`b75f9a1d398de4636e4494f2aaa04977326ca66a96356fcc1be87e86a3a520c4`.
The current parser reproduced:

- `obj_dataframe_60c91184df02`;
- object hash
  `60c91184df022d34cb4f8c5f7ae9444dc3abbd41f069e694329edc75b93d357c`;
- the exact 47-byte normalized payload;
- normalized SHA-256
  `d9067205ffb2aba89112d17662fef3eeaca2dabc0ba02a2a4a00063a24561daf`;
- one row with `formula` and `value`.

Only the three already-authoritative keys were conditionally created. Independent MinIO
readback, checksum validation and `DurableObjectStoreResolver` resolution passed. No
ScientificObjectVersion, ScientificResult or Report authority was written.

The current authenticated acceptance inventory is:

```text
Datasets = 28
READY = 17
EMPTY = 11
failed = 0

visible ScientificObject versions = 13
viewer HTTP failures = 0
payload READY = 13
support PROFESSIONAL = 13
SOURCE_MISSING = 0
```

The previously supplied trajectory screenshot was rechecked on exact object
`d325a090-d53f-4980-8a5e-c466bf6470eb`, version
`052d3a8e-8a35-48ac-9e65-b95a86b42c99`. The authenticated Viewer now renders the
three-frame trajectory with playback, picking, measurement, supercell and source metadata;
browser logs are empty.

Machine-readable recovery evidence:
`docs/agent2/product_maturity/evidence/exact_dataset_payload_recovery_2026-09-01.json`.
