# Data Visibility Closure — 2026-09-01

## Verdict

The reported unavailable scientific surfaces were not caused by a stopped
PostgreSQL, Redis, MinIO, API, worker, or frontend service.

Three separate product/data conditions were identified and closed:

1. Eleven legitimate zero-resource Datasets were being classified like storage
   failures by the object-store endpoint.
2. One historical user-visible Dataset had three absent MinIO objects even
   though PostgreSQL retained enough exact identity evidence to reconstruct and
   validate the original bytes.
3. The legacy Dataset detail route still exposed the old Analysis Planner for
   an empty Dataset, bypassing the professional empty-state contract used by the
   current Data Platform.

## Runtime

```text
frontend = http://127.0.0.1:3013
API = http://127.0.0.1:8005
database = PostgreSQL 127.0.0.1:55434
queue = Redis 127.0.0.1:6379/13
artifact storage = MinIO 127.0.0.1:9000 / mdi-artifacts
workers = 6 Redis-backed workers
provider = DeepSeek configured
```

`/health/runtime` reports every required component `ok`.

The final operations snapshot reports:

```text
status = ok
alerts = 0
PostgreSQL active = 1
PostgreSQL idle = 5
idle-in-transaction = 0
pool checkedOut = 0
stale user ResearchTurns = 0
stale user Jobs = 0
production queue depth = 0
workers = 6 idle
recent failed queue work = 0
MinIO = ok
```

## Exact Dataset Recovery

```text
Project = project_0001_d286007db78e427e
Dataset = dataset_0001_a0b09e3324e44ca4
Scientific object = obj_dataframe_60c91184df02
```

The exact 143-byte `materials.zip` was reconstructed from the authoritative test
input plus the persisted ZIP timestamp. Its SHA-256 exactly matches the
PostgreSQL reference:

```text
b75f9a1d398de4636e4494f2aaa04977326ca66a96356fcc1be87e86a3a520c4
```

The current parser reproduced the exact object ID, object hash and 47-byte
normalized JSON with SHA-256:

```text
d9067205ffb2aba89112d17662fef3eeaca2dabc0ba02a2a4a00063a24561daf
```

Only the three already-authoritative raw, normalized and metadata keys were
written. No ScientificObjectVersion, ScientificResult or Report was mutated,
and no newer source was substituted.

Browser result:

```text
rows = 1
formula = Si
value = 1
source unavailable message = false
global horizontal overflow = 0
browser errors = 0
```

Full byte-level evidence is preserved in
`docs/agent2/product_maturity/evidence/exact_dataset_payload_recovery_2026-09-01.json`.

## Visible Product Inventory

Authenticated acceptance-user scope:

```text
Projects = 16
Datasets = 28
  READY = 17
  EMPTY = 11
  failed/unavailable = 0

ScientificObjects = 13
ScientificObjectVersions = 13
Viewer READY = 13/13
Viewer SOURCE_MISSING = 0

completed/partial Results readable = 25/25
Artifact content readable = 241/241
Reports readable = 11/11
```

All current Structure, Trajectory, Band, DOS, Phonon Band, Phonon DOS and
Scientific Table renderers were exercised against visible exact versions.

Failed and canceled historical ResearchTurns remain honest terminal records;
they do not fabricate a ScientificResult.

## Empty Dataset Contract

The API now returns:

```json
{"resources": [], "availability": "EMPTY"}
```

for a Dataset with no files and no scientific objects.

The current Data Platform shows:

```text
尚未导入科学对象
```

with import guidance, no storage-failure language, no `研究此数据` action and no
Analysis Planner execution action.

Legacy `/projects/{projectId}/datasets/{datasetId}` routes redirect to:

```text
/projects/{projectId}/data?dataset={datasetId}
```

Project History links now use the current Data Platform route directly.

## Browser and Route Sweep

```text
authenticated product routes selected = 70
HTTP 200 = 70
failed = 0
Internal Server Error = 0
unexpected critical API failures = 0
browser console errors = 0
```

The old empty-Dataset deep link was additionally verified after the final 3013
build switch:

```text
redirected to current Data Platform = yes
professional empty state = yes
Research links = 0
Planner run actions = 0
global overflow = 0
browser logs = 0
```

## Regression

```text
full backend = 1970 passed, 84 historical/optional skipped
full frontend = 106 files, 773 passed
focused Dataset/Product frontend = 41 passed
focused object-store backend = 2 passed
production build = PASS
typecheck = PASS
compileall = PASS
uv lock --check = PASS
touched Ruff = PASS
git diff --check = PASS
```

Mandatory isolated PostgreSQL/Redis/MinIO campaign:

```text
selected = 70
passed = 70
failed = 0
errors = 0
skipped = 0
```

The campaign used a dedicated PostgreSQL database, Redis DB 15 and MinIO
bucket. All three exact qualification resources were removed after evidence was
captured; the live `mdi` database and `mdi-artifacts` bucket were not modified
by the isolated campaign.

## Remaining Storage Classification

Forty-four broken references belong to synthetic, inaccessible integration-test
projects that persisted placeholder `checksum-*` ScientificObjectVersion rows
without uploading corresponding bytes. Two additional old Artifacts declare
local test storage rather than MinIO.

They are not visible acceptance-user scientific data and were not fabricated or
silently repaired. Future service campaigns must continue using disposable
databases/buckets so this fixture residue does not grow in the shared runtime.

## Final User-Visible Status

```text
SERVICE_OUTAGE = NO
VISIBLE_DATASETS_READY_OR_EMPTY = 28/28
VISIBLE_VIEWERS_READY = 13/13
VISIBLE_ARTIFACTS_READABLE = 241/241
VISIBLE_REPORTS_READABLE = 11/11
INTERNAL_SERVER_ERROR = 0
SOURCE_MISSING = 0
SILENT_LATEST_SUBSTITUTION = NO
```
